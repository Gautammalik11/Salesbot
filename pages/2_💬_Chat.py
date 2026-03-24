"""
Chat Interface Page
Natural language query interface for sales data.
"""

import streamlit as st
import pandas as pd
from utils.query_engine import get_query_engine
from config.settings import settings
from auth.auth_manager import require_auth


st.set_page_config(
    page_title="Chat - Sales Chatbot",
    page_icon="💬",
    layout="wide"
)


def init_chat_state():
    """Initialize chat session state."""
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []

    if 'query_engine' not in st.session_state:
        try:
            st.session_state.query_engine = get_query_engine()
            st.session_state.query_engine_ready = True
        except Exception as e:
            st.session_state.query_engine_ready = False
            st.session_state.query_engine_error = str(e)


def display_chat_message(role: str, content: str, sql_query: str = None, results_df: pd.DataFrame = None):
    """Display a chat message.

    Args:
        role: 'user' or 'assistant'
        content: Message content
        sql_query: SQL query (for assistant messages)
        results_df: Results dataframe (for assistant messages)
    """
    with st.chat_message(role):
        st.markdown(content)

        if sql_query:
            with st.expander("🔍 View SQL Query", expanded=False):
                st.code(sql_query, language='sql')

        if results_df is not None and not results_df.empty:
            if len(results_df) <= 20:
                st.dataframe(results_df, use_container_width=True, hide_index=True)
            else:
                st.dataframe(results_df, use_container_width=True, hide_index=True, height=400)
                st.caption(f"Showing all {len(results_df)} results")


def process_query(question: str):
    """Process user query and get response.

    Args:
        question: User's question
    """
    # Add user message to chat
    st.session_state.chat_messages.append({
        'role': 'user',
        'content': question
    })

    # Get response from query engine
    with st.spinner("Thinking..."):
        result = st.session_state.query_engine.natural_language_query(question)

    if result['success']:
        # Format response
        response = result.get('response', 'Here are your results:')

        # Convert results to DataFrame
        results_df = pd.DataFrame(result['results']) if result['results'] else None

        # Add assistant message to chat
        st.session_state.chat_messages.append({
            'role': 'assistant',
            'content': response,
            'sql_query': result['sql_query'],
            'results': results_df
        })

    else:
        # Error response
        error_message = f"Sorry, I encountered an error: {result['error']}"

        if result.get('sql_query'):
            error_message += "\n\nThe generated SQL query might have an issue."

        st.session_state.chat_messages.append({
            'role': 'assistant',
            'content': error_message,
            'sql_query': result.get('sql_query')
        })


def main():
    """Main chat page logic."""
    require_auth()
    st.title("💬 Chat with Your Sales Data")

    # Initialize chat state
    init_chat_state()

    # Check if query engine is ready
    if not st.session_state.query_engine_ready:
        st.error("❌ Query engine initialization failed!")
        st.error(st.session_state.query_engine_error)

        st.info("""
        **Possible issues:**
        - Anthropic API key not configured in `.env` file
        - Invalid API key format
        - Database not initialized

        Please check your configuration and restart the application.
        """)
        st.stop()

    st.markdown("""
    Ask questions about your sales data in natural language. The AI will convert your question into SQL and provide results.
    """)

    st.markdown("---")

    # Example questions
    with st.expander("💡 Example Questions", expanded=False):
        st.markdown("""
        **Revenue & Sales:**
        - What is the total revenue?
        - Show me revenue by month for the last 6 months
        - Compare total sales between Odoo and Focus

        **Customer Insights:**
        - Who are my top 10 customers by revenue?
        - Which customers haven't ordered in the last 90 days?
        - Show me all purchases by ABC Corp

        **Product Analysis:**
        - What are my best-selling products?
        - Which product generated the most revenue?
        - List all products from Odoo

        **Invoice Details:**
        - Show me all invoices from January 2024
        - What is the average invoice amount?
        - Show me the highest value invoice
        - How many invoices do we have?
        """)

        # Quick question buttons
        st.markdown("**Try these quick questions:**")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💰 Total Revenue", use_container_width=True):
                process_query("What is the total revenue?")
                st.rerun()

        with col2:
            if st.button("👥 Top Customers", use_container_width=True):
                process_query("Show me top 10 customers by revenue")
                st.rerun()

        with col3:
            if st.button("📦 Top Products", use_container_width=True):
                process_query("What are my best-selling products?")
                st.rerun()

    st.markdown("---")

    # Chat container
    chat_container = st.container()

    with chat_container:
        # Display chat history
        for message in st.session_state.chat_messages:
            display_chat_message(
                role=message['role'],
                content=message['content'],
                sql_query=message.get('sql_query'),
                results_df=message.get('results')
            )

    # Chat input
    question = st.chat_input("Ask a question about your sales data...")

    if question:
        # Display user message immediately
        with chat_container:
            display_chat_message('user', question)

        # Process query
        process_query(question)

        # Rerun to update chat
        st.rerun()

    # Sidebar with controls
    with st.sidebar:
        st.markdown("### 🎛️ Chat Controls")

        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

        st.markdown("---")

        st.markdown("### 📊 Chat Statistics")
        total_messages = len(st.session_state.chat_messages)
        user_messages = sum(1 for m in st.session_state.chat_messages if m['role'] == 'user')

        st.metric("Total Messages", total_messages)
        st.metric("Your Questions", user_messages)

        st.markdown("---")

        st.markdown("### 💡 Tips")
        st.markdown("""
        - Be specific in your questions
        - Use customer/product names exactly as in your data
        - You can ask follow-up questions
        - Check the SQL query to understand how data was retrieved
        - Use date formats like "2024-01", "last month", "this year"
        """)

        st.markdown("---")

        st.markdown("### ⚙️ Database Schema")

        if st.button("📋 View Schema", use_container_width=True):
            schema_info = st.session_state.query_engine.get_schema_info()
            st.text_area("Database Schema", schema_info, height=300)

    # Empty state
    if len(st.session_state.chat_messages) == 0:
        st.info("👋 Start by asking a question about your sales data!")

        st.markdown("### 🚀 Quick Start")

        st.markdown("""
        1. Type your question in the chat input below
        2. Press Enter or click Send
        3. View the AI-generated SQL query (optional)
        4. See your results in a table

        **Example:** "Show me top 5 customers by revenue"
        """)


if __name__ == "__main__":
    main()
