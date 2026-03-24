"""
Analytics Module for Sales Data
Pre-built analytics functions for common business queries.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from database.db_manager import get_db_manager


class SalesAnalytics:
    """Pre-built analytics functions for sales data."""

    def __init__(self):
        """Initialize analytics module."""
        self.db = get_db_manager()

    def get_total_revenue(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        erp: Optional[str] = None
    ) -> float:
        """Get total revenue within date range.

        Args:
            start_date: Start date (YYYY-MM-DD) (optional)
            end_date: End date (YYYY-MM-DD) (optional)
            erp: Deprecated, kept for compatibility

        Returns:
            Total revenue as float
        """
        query = "SELECT SUM(total_amount) as total FROM sales WHERE 1=1"
        params = []

        if start_date:
            query += " AND invoice_date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND invoice_date <= ?"
            params.append(end_date)

        result = self.db.execute_query(query, tuple(params))
        return result[0]['total'] if result and result[0]['total'] else 0.0

    def get_top_customers(
        self,
        n: int = 10,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        erp: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get top N customers by revenue.

        Args:
            n: Number of top customers to return
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            erp: Deprecated, kept for compatibility

        Returns:
            List of dictionaries with customer data
        """
        query = """
            SELECT
                c.customer_name,
                COUNT(DISTINCT s.id) as sales_count,
                SUM(s.total_amount) as total_revenue
            FROM customers c
            JOIN sales s ON c.id = s.customer_id
            WHERE 1=1
        """
        params = []

        if start_date:
            query += " AND s.invoice_date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND s.invoice_date <= ?"
            params.append(end_date)

        query += """
            GROUP BY c.customer_name
            ORDER BY total_revenue DESC
            LIMIT ?
        """
        params.append(n)

        return self.db.execute_query(query, tuple(params))

    def get_top_products(
        self,
        n: int = 10,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        erp: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get top N products by sales.

        Args:
            n: Number of top products to return
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            erp: Deprecated, kept for compatibility

        Returns:
            List of dictionaries with product data
        """
        query = """
            SELECT
                p.item_name as product_name,
                SUM(s.quantity) as total_quantity,
                SUM(s.total_amount) as total_revenue
            FROM products p
            JOIN sales s ON p.id = s.product_id
            WHERE 1=1
        """
        params = []

        if start_date:
            query += " AND s.invoice_date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND s.invoice_date <= ?"
            params.append(end_date)

        query += """
            GROUP BY p.item_name
            ORDER BY total_revenue DESC
            LIMIT ?
        """
        params.append(n)

        return self.db.execute_query(query, tuple(params))

    def get_revenue_by_month(
        self,
        months: int = 12,
        erp: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get revenue trend by month.

        Args:
            months: Number of months to include
            erp: Deprecated, kept for compatibility

        Returns:
            List of dictionaries with monthly revenue
        """
        query = """
            SELECT
                strftime('%Y-%m', invoice_date) as month,
                SUM(total_amount) as revenue,
                COUNT(*) as sales_count
            FROM sales
            WHERE invoice_date IS NOT NULL
            GROUP BY month
            ORDER BY month DESC
            LIMIT ?
        """
        params = [months]

        results = self.db.execute_query(query, tuple(params))
        return list(reversed(results))  # Chronological order

    def get_erp_comparison(self) -> Dict[str, Any]:
        """Deprecated - no longer tracks ERP distinction in v2.

        Returns:
            Empty dictionary (kept for compatibility)
        """
        # No longer tracking ERP distinction in v2
        return {}

    def get_customer_purchase_history(
        self,
        customer_name: str,
        erp: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed purchase history for a specific customer.

        Args:
            customer_name: Customer name
            erp: Deprecated, kept for compatibility

        Returns:
            Dictionary with customer details and purchase history
        """
        # Get customer summary
        query = """
            SELECT
                c.customer_name,
                COUNT(DISTINCT s.id) as total_sales,
                SUM(s.total_amount) as total_spent,
                MIN(s.invoice_date) as first_purchase,
                MAX(s.invoice_date) as last_purchase
            FROM customers c
            JOIN sales s ON c.id = s.customer_id
            WHERE c.customer_name = ?
            GROUP BY c.customer_name
        """
        params = [customer_name]

        summary = self.db.execute_query(query, tuple(params))

        if not summary:
            return None

        # Get sales details
        sales_query = """
            SELECT
                s.voucher_no,
                s.invoice_date,
                s.total_amount,
                p.item_name as product
            FROM sales s
            JOIN customers c ON s.customer_id = c.id
            JOIN products p ON s.product_id = p.id
            WHERE c.customer_name = ?
            ORDER BY s.invoice_date DESC
        """
        sales_params = [customer_name]

        sales = self.db.execute_query(sales_query, tuple(sales_params))

        return {
            'summary': summary[0],
            'sales': sales
        }

    def get_inactive_customers(
        self,
        days: int = 90,
        erp: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get customers with no recent orders.

        Args:
            days: Number of days to define inactivity
            erp: Deprecated, kept for compatibility

        Returns:
            List of inactive customers
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        query = """
            SELECT
                c.customer_name,
                MAX(s.invoice_date) as last_purchase,
                SUM(s.total_amount) as lifetime_value
            FROM customers c
            JOIN sales s ON c.id = s.customer_id
            GROUP BY c.customer_name
            HAVING MAX(s.invoice_date) < ?
            ORDER BY last_purchase DESC
        """
        params = [cutoff_date]

        return self.db.execute_query(query, tuple(params))

    def get_summary_metrics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        erp: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get summary metrics for dashboard.

        Args:
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            erp: Deprecated, kept for compatibility

        Returns:
            Dictionary with key metrics
        """
        query = """
            SELECT
                COUNT(DISTINCT s.customer_id) as customer_count,
                COUNT(DISTINCT s.product_id) as product_count,
                COUNT(DISTINCT s.id) as sales_count,
                SUM(s.total_amount) as total_revenue,
                AVG(s.total_amount) as avg_sale
            FROM sales s
            WHERE 1=1
        """
        params = []

        if start_date:
            query += " AND s.invoice_date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND s.invoice_date <= ?"
            params.append(end_date)

        result = self.db.execute_query(query, tuple(params) if params else None)
        return result[0] if result else {}

    def get_sales_by_day_of_week(
        self,
        erp: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get sales distribution by day of week.

        Args:
            erp: Deprecated, kept for compatibility

        Returns:
            List with sales by day of week
        """
        query = """
            SELECT
                CASE CAST(strftime('%w', invoice_date) AS INTEGER)
                    WHEN 0 THEN 'Sunday'
                    WHEN 1 THEN 'Monday'
                    WHEN 2 THEN 'Tuesday'
                    WHEN 3 THEN 'Wednesday'
                    WHEN 4 THEN 'Thursday'
                    WHEN 5 THEN 'Friday'
                    WHEN 6 THEN 'Saturday'
                END as day_of_week,
                COUNT(*) as sales_count,
                SUM(total_amount) as revenue
            FROM sales
            WHERE invoice_date IS NOT NULL
            GROUP BY strftime('%w', invoice_date)
            ORDER BY CAST(strftime('%w', invoice_date) AS INTEGER)
        """

        return self.db.execute_query(query)


# Singleton instance
_analytics = None

def get_analytics() -> SalesAnalytics:
    """Get singleton analytics instance.

    Returns:
        SalesAnalytics instance
    """
    global _analytics
    if _analytics is None:
        _analytics = SalesAnalytics()
    return _analytics
