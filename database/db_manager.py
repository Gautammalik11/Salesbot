"""
Database Manager v2 for Sales & Quotation Chatbot
Handles sales data and quotations without ERP distinction.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime


class DatabaseManager:
    """Manages SQLite database operations for sales and quotation data."""

    def __init__(self, db_path: str = "database/sales.db"):
        """Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.schema_path = "database/schema.sql"

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection.

        Returns:
            SQLite connection object
        """
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self) -> None:
        """Initialize database with schema from schema_v2.sql file."""
        if not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

        with open(self.schema_path, 'r') as f:
            schema_sql = f.read()

        conn = self.get_connection()
        try:
            conn.executescript(schema_sql)
            conn.commit()
            print("Database initialized successfully with new schema!")
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise
        finally:
            conn.close()

    def upsert_customer(
        self,
        customer_name: str,
        gst_no: Optional[str] = None,
        branch: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        mobile_no: Optional[str] = None,
        email_id: Optional[str] = None
    ) -> int:
        """Insert or update customer and return customer ID.

        Args:
            customer_name: Customer name
            gst_no: GST number (optional)
            branch: Branch name (optional)
            state: State (optional)
            city: City (optional)
            mobile_no: Mobile number (optional)
            email_id: Email ID (optional)

        Returns:
            Customer ID
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO customers (customer_name, gst_no, branch, state, city, mobile_no, email_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(customer_name) DO UPDATE SET
                    gst_no = COALESCE(excluded.gst_no, gst_no),
                    branch = COALESCE(excluded.branch, branch),
                    state = COALESCE(excluded.state, state),
                    city = COALESCE(excluded.city, city),
                    mobile_no = COALESCE(excluded.mobile_no, mobile_no),
                    email_id = COALESCE(excluded.email_id, email_id),
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
                """,
                (customer_name, gst_no, branch, state, city, mobile_no, email_id)
            )
            customer_id = cursor.fetchone()[0]
            conn.commit()
            return customer_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def upsert_product(
        self,
        item_name: str,
        item_group: Optional[str] = None,
        item_code: Optional[str] = None
    ) -> int:
        """Insert or get product ID.

        Args:
            item_name: Product/item name
            item_group: Item group (optional)
            item_code: Item code (optional)

        Returns:
            Product ID
        """
        conn = self.get_connection()
        try:
            # Try to insert
            cursor = conn.execute(
                """
                INSERT INTO products (item_name, item_group, item_code)
                VALUES (?, ?, ?)
                ON CONFLICT(item_name, item_code) DO UPDATE SET
                    item_group = COALESCE(excluded.item_group, item_group)
                RETURNING id
                """,
                (item_name, item_group, item_code)
            )

            product_id = cursor.fetchone()[0]
            conn.commit()
            return product_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def insert_sale(self, sale_data: Dict[str, Any]) -> int:
        """Insert sales record with all fields.

        Args:
            sale_data: Dictionary with all sales fields

        Returns:
            Sale ID
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO sales (
                    customer_id, product_id, invoice_date, due_date, customer_po_date,
                    voucher_no, customer_po_no, excise_inv_no, account_code, payment_terms,
                    rma, batch_number, quantity, selling_rate, selling_gross, discount_percent,
                    net_rate, discount_percent_2, net_gross, packing_forwarding, freight,
                    insurance, assessable_value, cgst, sgst, igst, total_amount,
                    engineer, transporter, units, freight_term, tax_master, form_type, links
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sale_data.get('customer_id'),
                    sale_data.get('product_id'),
                    sale_data.get('invoice_date'),
                    sale_data.get('due_date'),
                    sale_data.get('customer_po_date'),
                    sale_data.get('voucher_no'),
                    sale_data.get('customer_po_no'),
                    sale_data.get('excise_inv_no'),
                    sale_data.get('account_code'),
                    sale_data.get('payment_terms'),
                    sale_data.get('rma'),
                    sale_data.get('batch_number'),
                    sale_data.get('quantity'),
                    sale_data.get('selling_rate'),
                    sale_data.get('selling_gross'),
                    sale_data.get('discount_percent'),
                    sale_data.get('net_rate'),
                    sale_data.get('discount_percent_2'),
                    sale_data.get('net_gross'),
                    sale_data.get('packing_forwarding'),
                    sale_data.get('freight'),
                    sale_data.get('insurance'),
                    sale_data.get('assessable_value'),
                    sale_data.get('cgst'),
                    sale_data.get('sgst'),
                    sale_data.get('igst'),
                    sale_data.get('total_amount'),
                    sale_data.get('engineer'),
                    sale_data.get('transporter'),
                    sale_data.get('units'),
                    sale_data.get('freight_term'),
                    sale_data.get('tax_master'),
                    sale_data.get('form_type'),
                    sale_data.get('links')
                )
            )
            sale_id = cursor.lastrowid
            conn.commit()
            return sale_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def insert_quotation(self, quotation_data: Dict[str, Any]) -> int:
        """Insert quotation record.

        Args:
            quotation_data: Dictionary with quotation fields

        Returns:
            Quotation ID
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO quotations (
                    customer_id, creation_date, order_reference, status, salesperson,
                    product_name, quantity, unit_price, discount_percent, untaxed_amount
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    quotation_data.get('customer_id'),
                    quotation_data.get('creation_date'),
                    quotation_data.get('order_reference'),
                    quotation_data.get('status'),
                    quotation_data.get('salesperson'),
                    quotation_data.get('product_name'),
                    quotation_data.get('quantity'),
                    quotation_data.get('unit_price'),
                    quotation_data.get('discount_percent'),
                    quotation_data.get('untaxed_amount')
                )
            )
            quotation_id = cursor.lastrowid
            conn.commit()
            return quotation_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """Execute SQL query safely with parameterization.

        Args:
            query: SQL query string
            params: Query parameters (optional)

        Returns:
            List of result rows as dictionaries
        """
        conn = self.get_connection()
        try:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)

            columns = [description[0] for description in cursor.description] if cursor.description else []
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return results
        except Exception as e:
            raise e
        finally:
            conn.close()

    def get_schema_info(self) -> str:
        """Get database schema information for LLM context.

        Returns:
            Formatted schema information as string
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            tables = [row[0] for row in cursor.fetchall()]

            schema_info = """Database Schema:

IMPORTANT RELATIONSHIPS:
- sales.customer_id → customers.id (each sale belongs to a customer)
- sales.product_id → products.id (each sale has a product)
- quotations.customer_id → customers.id (each quotation belongs to a customer)

TABLE DESCRIPTIONS:
- customers: Contains customer information (name, contact details, GST, location)
- products: Contains product/item information (name, group, code)
- sales: Contains actual sales/invoice records with all financial details
- quotations: Contains quotation/proposal records (may or may not convert to sales)

COMMON PATTERNS:
- To get sales for a customer: JOIN sales with customers on customer_id
- To get quotations for a customer: JOIN quotations with customers on customer_id
- To get both sales AND quotations: Use UNION or separate queries
- Product names in sales table: JOIN sales with products.item_name
- Product names in quotations table: Use quotations.product_name directly

"""

            for table in tables:
                schema_info += f"Table: {table}\n"
                cursor = conn.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()

                for col in columns:
                    col_name = col[1]
                    col_type = col[2]
                    is_pk = " (PRIMARY KEY)" if col[5] else ""
                    not_null = " NOT NULL" if col[3] else ""
                    schema_info += f"  - {col_name}: {col_type}{is_pk}{not_null}\n"

                schema_info += "\n"

            return schema_info
        finally:
            conn.close()

    def get_table_stats(self) -> Dict[str, int]:
        """Get record counts for all tables.

        Returns:
            Dictionary with table names and record counts
        """
        conn = self.get_connection()
        try:
            stats = {}
            tables = ['customers', 'products', 'sales', 'quotations']

            for table in tables:
                try:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[table] = cursor.fetchone()[0]
                except:
                    stats[table] = 0

            return stats
        finally:
            conn.close()


# Singleton instance
_db_manager = None

def get_db_manager(db_path: str = "database/sales.db") -> DatabaseManager:
    """Get singleton database manager instance.

    Args:
        db_path: Path to database file

    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_path)
    return _db_manager
