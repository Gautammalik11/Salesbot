"""
Database Manager - Supports both SQLite (local) and PostgreSQL (Supabase).
Set DATABASE_URL in .env to use Supabase. Leave unset to use SQLite locally.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:

    def __init__(self):
        database_url = os.getenv("DATABASE_URL", "")
        db_path = os.getenv("DATABASE_PATH", "database/sales.db")

        if database_url:
            self.engine = create_engine(database_url, pool_pre_ping=True)
            self.db_type = "postgresql"
        else:
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            self.engine = create_engine(
                f"sqlite:///{db_path}",
                connect_args={"check_same_thread": False}
            )
            self.db_type = "sqlite"

    def init_database(self) -> None:
        if self.db_type == "postgresql":
            # Tables are created via Supabase SQL Editor using schema_supabase.sql
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("PostgreSQL connection verified!")
        else:
            schema_path = "database/schema.sql"
            if not os.path.exists(schema_path):
                raise FileNotFoundError(f"Schema file not found: {schema_path}")
            with open(schema_path, "r") as f:
                schema_sql = f.read()
            with self.engine.begin() as conn:
                for stmt in schema_sql.split(";"):
                    if stmt.strip():
                        conn.execute(text(stmt))
            print("SQLite database initialized!")

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
        params = {
            "customer_name": customer_name,
            "gst_no": gst_no,
            "branch": branch,
            "state": state,
            "city": city,
            "mobile_no": mobile_no,
            "email_id": email_id,
        }
        with self.engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO customers (customer_name, gst_no, branch, state, city, mobile_no, email_id)
                VALUES (:customer_name, :gst_no, :branch, :state, :city, :mobile_no, :email_id)
                ON CONFLICT(customer_name) DO NOTHING
            """), params)
            conn.execute(text("""
                UPDATE customers SET
                    gst_no = COALESCE(:gst_no, gst_no),
                    branch = COALESCE(:branch, branch),
                    state = COALESCE(:state, state),
                    city = COALESCE(:city, city),
                    mobile_no = COALESCE(:mobile_no, mobile_no),
                    email_id = COALESCE(:email_id, email_id)
                WHERE customer_name = :customer_name
            """), params)
            result = conn.execute(
                text("SELECT id FROM customers WHERE customer_name = :customer_name"),
                {"customer_name": customer_name}
            )
            return result.scalar()

    def upsert_product(
        self,
        item_name: str,
        item_group: Optional[str] = None,
        item_code: Optional[str] = None
    ) -> int:
        params = {
            "item_name": item_name,
            "item_group": item_group,
            "item_code": item_code,
        }
        with self.engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO products (item_name, item_group, item_code)
                VALUES (:item_name, :item_group, :item_code)
                ON CONFLICT(item_name) DO NOTHING
            """), params)
            conn.execute(text("""
                UPDATE products SET
                    item_group = COALESCE(:item_group, item_group),
                    item_code = COALESCE(:item_code, item_code)
                WHERE item_name = :item_name
            """), params)
            result = conn.execute(
                text("SELECT id FROM products WHERE item_name = :item_name"),
                {"item_name": item_name}
            )
            return result.scalar()

    def insert_sale(self, sale_data: Dict[str, Any]) -> None:
        with self.engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO sales (
                    customer_id, product_id, invoice_date, due_date, customer_po_date,
                    voucher_no, customer_po_no, excise_inv_no, account_code, payment_terms,
                    rma, batch_number, quantity, selling_rate, selling_gross, discount_percent,
                    net_rate, discount_percent_2, net_gross, packing_forwarding, freight,
                    insurance, assessable_value, cgst, sgst, igst, total_amount,
                    engineer, transporter, units, freight_term, tax_master, form_type, links
                ) VALUES (
                    :customer_id, :product_id, :invoice_date, :due_date, :customer_po_date,
                    :voucher_no, :customer_po_no, :excise_inv_no, :account_code, :payment_terms,
                    :rma, :batch_number, :quantity, :selling_rate, :selling_gross, :discount_percent,
                    :net_rate, :discount_percent_2, :net_gross, :packing_forwarding, :freight,
                    :insurance, :assessable_value, :cgst, :sgst, :igst, :total_amount,
                    :engineer, :transporter, :units, :freight_term, :tax_master, :form_type, :links
                )
            """), {k: sale_data.get(k) for k in [
                'customer_id', 'product_id', 'invoice_date', 'due_date', 'customer_po_date',
                'voucher_no', 'customer_po_no', 'excise_inv_no', 'account_code', 'payment_terms',
                'rma', 'batch_number', 'quantity', 'selling_rate', 'selling_gross', 'discount_percent',
                'net_rate', 'discount_percent_2', 'net_gross', 'packing_forwarding', 'freight',
                'insurance', 'assessable_value', 'cgst', 'sgst', 'igst', 'total_amount',
                'engineer', 'transporter', 'units', 'freight_term', 'tax_master', 'form_type', 'links'
            ]})

    def insert_quotation(self, quotation_data: Dict[str, Any]) -> None:
        with self.engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO quotations (
                    customer_id, creation_date, order_reference, status, salesperson,
                    product_name, quantity, unit_price, discount_percent, untaxed_amount
                ) VALUES (
                    :customer_id, :creation_date, :order_reference, :status, :salesperson,
                    :product_name, :quantity, :unit_price, :discount_percent, :untaxed_amount
                )
            """), {k: quotation_data.get(k) for k in [
                'customer_id', 'creation_date', 'order_reference', 'status', 'salesperson',
                'product_name', 'quantity', 'unit_price', 'discount_percent', 'untaxed_amount'
            ]})

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            if result.returns_rows:
                columns = list(result.keys())
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            return []

    def get_schema_info(self) -> str:
        known_tables = ['customers', 'products', 'sales', 'quotations']
        schema_info = """Database Schema:

IMPORTANT RELATIONSHIPS:
- sales.customer_id → customers.id
- sales.product_id → products.id
- quotations.customer_id → customers.id

TABLE DESCRIPTIONS:
- customers: Customer info (name, GST, contact, location)
- products: Product/item info (name, group, code)
- sales: Actual invoices/sales records with all financial columns
- quotations: Quotation/proposal records (may or may not convert to sales)

COMMON QUERY PATTERNS:
- Sales for a customer: JOIN sales s ON s.customer_id = c.id, JOIN customers c
- Quotations for a customer: JOIN quotations q ON q.customer_id = c.id
- Both sales + quotations: Use UNION ALL with record_type column
- Product name in sales: JOIN products p ON s.product_id = p.id → p.item_name
- Product name in quotations: q.product_name (stored directly)

"""
        try:
            with self.engine.connect() as conn:
                for table in known_tables:
                    schema_info += f"Table: {table}\n"
                    if self.db_type == "postgresql":
                        result = conn.execute(text("""
                            SELECT column_name, data_type
                            FROM information_schema.columns
                            WHERE table_schema = 'public' AND table_name = :table
                            ORDER BY ordinal_position
                        """), {"table": table})
                        for row in result.fetchall():
                            schema_info += f"  - {row[0]}: {row[1]}\n"
                    else:
                        result = conn.execute(text(f"PRAGMA table_info({table})"))
                        for row in result.fetchall():
                            pk = " (PRIMARY KEY)" if row[5] else ""
                            schema_info += f"  - {row[1]}: {row[2]}{pk}\n"
                    schema_info += "\n"
        except Exception as e:
            schema_info += f"(Error reading schema: {e})\n"
        return schema_info

    def get_table_stats(self) -> Dict[str, int]:
        stats = {}
        for table in ['customers', 'products', 'sales', 'quotations']:
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    stats[table] = result.scalar()
            except Exception:
                stats[table] = 0
        return stats

    def clear_all_data(self) -> None:
        with self.engine.begin() as conn:
            conn.execute(text("DELETE FROM sales"))
            conn.execute(text("DELETE FROM quotations"))
            conn.execute(text("DELETE FROM products"))
            conn.execute(text("DELETE FROM customers"))


# Singleton
_db_manager = None


def get_db_manager() -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
