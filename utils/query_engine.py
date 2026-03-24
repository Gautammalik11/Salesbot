"""
Query Engine for Natural Language to SQL conversion.
Uses LangChain and Claude API to convert user questions into SQL queries.
"""

from typing import Dict, Any, Optional, Tuple
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from config.settings import settings
from database.db_manager import get_db_manager
import re


class QueryEngine:
    """Natural language query engine for sales data."""

    def __init__(self):
        """Initialize query engine."""
        self.db_manager = get_db_manager()

        # Validate API key
        try:
            settings.validate()
        except ValueError as e:
            raise ValueError(f"Configuration error: {e}")

        # Initialize Claude LLM
        self.llm = ChatAnthropic(
            model=settings.CLAUDE_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=settings.CLAUDE_TEMPERATURE
        )

        # Initialize SQLDatabase for LangChain
        db_url = settings.get_database_url()
        self.sql_database = SQLDatabase.from_uri(db_url)

        # Create SQL query chain with custom prompt for better context
        from langchain_core.prompts import PromptTemplate

        custom_prompt = PromptTemplate.from_template("""
You are a SQL expert. Create a syntactically correct SQLite query based on the question.

CRITICAL RULES:
1. When asked about a CUSTOMER (by name or info request), ALWAYS query BOTH 'sales' AND 'quotations' tables using UNION ALL
2. Include a 'record_type' column to distinguish 'Sale' from 'Quotation'
3. Show comprehensive columns: customer_name, date, reference/voucher, product, quantity, price, amount
4. ALWAYS use JOINs with customers table (and products table for sales)

DATABASE STRUCTURE:
- 'sales' table: Actual sales/invoices with 30+ columns (voucher_no, invoice_date, total_amount, etc.)
- 'quotations' table: Quotation/proposal records (order_reference, creation_date, untaxed_amount, etc.)
- Both link to 'customers' via customer_id
- Sales links to 'products' via product_id (use products.item_name)
- Quotations have product_name stored directly

REQUIRED QUERY PATTERN FOR CUSTOMER QUERIES:
```
SELECT 'Sale' as record_type, c.customer_name, s.invoice_date as date,
       s.voucher_no as reference, p.item_name as product, s.quantity,
       s.selling_rate as price, s.total_amount
FROM sales s
JOIN customers c ON s.customer_id = c.id
JOIN products p ON s.product_id = p.id
WHERE c.customer_name LIKE '%CustomerName%'

UNION ALL

SELECT 'Quotation' as record_type, c.customer_name, q.creation_date as date,
       q.order_reference as reference, q.product_name as product, q.quantity,
       q.unit_price as price, q.untaxed_amount as total_amount
FROM quotations q
JOIN customers c ON q.customer_id = c.id
WHERE c.customer_name LIKE '%CustomerName%'
```

Schema:
{table_info}

Question: {input}

Unless otherwise specified, limit results to {top_k} rows.
Return ONLY the SQL query, no explanation.
""")

        self.query_chain = create_sql_query_chain(
            self.llm,
            self.sql_database,
            prompt=custom_prompt
        )

        # Create query execution tool
        self.execute_query_tool = QuerySQLDataBaseTool(db=self.sql_database)

    def _clean_sql_query(self, query: str) -> str:
        """Clean generated SQL query.

        Args:
            query: Raw SQL query

        Returns:
            Cleaned SQL query
        """
        # Remove markdown code blocks if present
        query = re.sub(r'```sql\s*', '', query)
        query = re.sub(r'```\s*', '', query)

        # Extract SQL query from text (handle cases where LLM adds explanation)
        # Look for SELECT statement (case insensitive)
        select_match = re.search(r'(SELECT\s+.*?;)', query, re.IGNORECASE | re.DOTALL)
        if select_match:
            query = select_match.group(1)

        # If no semicolon found, try to extract until end of string
        if not select_match:
            select_match = re.search(r'(SELECT\s+.*)', query, re.IGNORECASE | re.DOTALL)
            if select_match:
                query = select_match.group(1)

        # Remove extra whitespace
        query = ' '.join(query.split())

        # Ensure query ends with semicolon
        query = query.strip()
        if not query.endswith(';'):
            query += ';'

        return query

    def _validate_sql_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate SQL query for safety.

        Args:
            query: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        query_lower = query.lower()

        # Only allow SELECT queries
        if not query_lower.strip().startswith('select'):
            return False, "Only SELECT queries are allowed for safety reasons."

        # Disallow dangerous operations
        dangerous_keywords = ['drop', 'delete', 'insert', 'update', 'alter', 'create', 'truncate']
        for keyword in dangerous_keywords:
            if keyword in query_lower:
                return False, f"Query contains dangerous keyword: {keyword}"

        return True, None

    def natural_language_query(self, question: str) -> Dict[str, Any]:
        """Convert natural language question to SQL and execute.

        Args:
            question: User's question in natural language

        Returns:
            Dictionary with query results, SQL, and metadata
        """
        try:
            # Detect if user wants all results (no limit)
            question_lower = question.lower()
            wants_all = any(keyword in question_lower for keyword in ['all', 'every', 'complete', 'full'])

            # Set appropriate top_k based on query intent
            top_k = 10000 if wants_all else 100  # Increased from default 5 to 100

            # Generate SQL query from natural language
            sql_query = self.query_chain.invoke({
                "question": question,
                "top_k": top_k
            })

            # Clean the query
            sql_query = self._clean_sql_query(sql_query)

            # Validate query
            is_valid, error_msg = self._validate_sql_query(sql_query)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg,
                    'sql_query': sql_query,
                    'results': []
                }

            # Execute query
            results = self.db_manager.execute_query(sql_query.rstrip(';'))

            # Generate natural language response
            response = self._generate_response(question, results)

            return {
                'success': True,
                'sql_query': sql_query,
                'results': results,
                'response': response,
                'row_count': len(results)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'sql_query': sql_query if 'sql_query' in locals() else None,
                'results': []
            }

    def _generate_response(self, question: str, results: list) -> str:
        """Generate natural language response from query results.

        Args:
            question: Original question
            results: Query results

        Returns:
            Natural language response
        """
        if not results:
            return "No results found for your query."

        # For simple queries, create a formatted response
        num_results = len(results)

        if num_results == 1 and len(results[0]) == 1:
            # Single value result
            value = list(results[0].values())[0]
            return f"The answer is: {value}"

        elif num_results <= 5:
            # Small result set - provide detailed answer
            return f"I found {num_results} result(s)."

        else:
            # Large result set - provide summary
            return f"I found {num_results} results. Showing all results in the table below."

    def get_schema_info(self) -> str:
        """Get database schema information.

        Returns:
            Schema information as string
        """
        return self.db_manager.get_schema_info()

    def suggest_questions(self) -> list:
        """Get list of suggested example questions.

        Returns:
            List of example questions
        """
        return [
            "Show me total revenue",
            "What are my top 10 customers by revenue?",
            "List the best-selling products",
            "How much revenue did we generate last month?",
            "Show me all customers from Odoo",
            "What is the average invoice amount?",
            "Which customers haven't ordered in the last 90 days?",
            "Compare total sales between Odoo and Focus",
            "Show me all invoices for customer [name]",
            "What products did customer [name] buy?",
            "Show me revenue trend by month",
            "List all invoices from 2024",
            "What is the total number of customers?",
            "Show me the highest value invoice",
            "Which product generated the most revenue?"
        ]

    def ask_with_context(self, question: str, chat_history: Optional[list] = None) -> Dict[str, Any]:
        """Ask a question with conversation context.

        Args:
            question: User's question
            chat_history: Previous conversation messages (optional)

        Returns:
            Query results dictionary
        """
        # For now, just use the simple query
        # Can be enhanced with conversation memory in the future
        return self.natural_language_query(question)


# Singleton instance
_query_engine = None

def get_query_engine() -> QueryEngine:
    """Get singleton query engine instance.

    Returns:
        QueryEngine instance
    """
    global _query_engine
    if _query_engine is None:
        _query_engine = QueryEngine()
    return _query_engine
