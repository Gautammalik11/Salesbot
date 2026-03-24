"""
Analytics Dashboard Page
Comprehensive analytics and insights for sales data.
"""

import streamlit as st
from datetime import datetime, timedelta
from utils.analytics import get_analytics
from utils.visualization import (
    create_bar_chart,
    create_horizontal_bar_chart,
    create_line_chart,
    create_pie_chart,
    format_currency
)
from config.settings import settings
from auth.auth_manager import require_auth


st.set_page_config(
    page_title="Analytics - Sales Chatbot",
    page_icon="📊",
    layout="wide"
)


def main():
    """Main analytics page logic."""
    require_auth()
    st.title("📊 Sales Analytics Dashboard")

    st.markdown("""
    Explore comprehensive analytics and insights about your sales data with interactive charts and metrics.
    """)

    # Initialize analytics
    analytics = get_analytics()

    st.markdown("---")

    # Filters
    st.markdown("### 🔍 Filters")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Date range filter
        date_filter = st.selectbox(
            "Date Range",
            options=[
                "All Time",
                "Last 7 Days",
                "Last 30 Days",
                "Last 90 Days",
                "Last 6 Months",
                "Last Year",
                "Custom Range"
            ],
            index=0
        )

        start_date = None
        end_date = None

        if date_filter == "Last 7 Days":
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        elif date_filter == "Last 30 Days":
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        elif date_filter == "Last 90 Days":
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        elif date_filter == "Last 6 Months":
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        elif date_filter == "Last Year":
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        elif date_filter == "Custom Range":
            col_a, col_b = st.columns(2)
            with col_a:
                start_date = st.date_input("Start Date").strftime('%Y-%m-%d')
            with col_b:
                end_date = st.date_input("End Date").strftime('%Y-%m-%d')

    with col2:
        # ERP filter
        erp_filter = st.selectbox(
            "ERP Source",
            options=["All", "Odoo", "Focus"],
            index=0
        )

        erp = None if erp_filter == "All" else erp_filter

    with col3:
        # Refresh button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    st.markdown("---")

    # Summary Metrics
    st.markdown("### 📈 Key Metrics")

    summary = analytics.get_summary_metrics(start_date, end_date, erp)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        revenue = summary.get('total_revenue', 0) or 0
        st.metric(
            "Total Revenue",
            format_currency(revenue, settings.CURRENCY_SYMBOL),
            help="Total revenue for selected period"
        )

    with col2:
        sales_count = summary.get('sales_count', 0) or 0
        st.metric(
            "Sales",
            f"{sales_count:,}",
            help="Total number of sales records"
        )

    with col3:
        customers = summary.get('customer_count', 0) or 0
        st.metric(
            "Customers",
            f"{customers:,}",
            help="Total unique customers"
        )

    with col4:
        avg_sale = summary.get('avg_sale', 0) or 0
        st.metric(
            "Avg Sale",
            format_currency(avg_sale, settings.CURRENCY_SYMBOL),
            help="Average sale amount"
        )

    st.markdown("---")

    # Charts - Row 1
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📅 Revenue Trend (Last 12 Months)")

        revenue_data = analytics.get_revenue_by_month(12, erp)

        if revenue_data:
            fig = create_line_chart(
                data=revenue_data,
                x_field='month',
                y_field='revenue',
                title='',
                x_label='Month',
                y_label=f'Revenue ({settings.CURRENCY_SYMBOL})',
                color='#00CC96'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for revenue trend")

    with col2:
        st.markdown("#### 👥 Top 10 Customers by Revenue")

        top_customers = analytics.get_top_customers(10, start_date, end_date, erp)

        if top_customers:
            fig = create_horizontal_bar_chart(
                data=top_customers,
                x_field='total_revenue',
                y_field='customer_name',
                title='',
                x_label=f'Revenue ({settings.CURRENCY_SYMBOL})',
                y_label='Customer',
                color='#636EFA'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No customer data available")

    st.markdown("---")

    # Charts - Row 2
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📦 Top 10 Products by Revenue")

        top_products = analytics.get_top_products(10, start_date, end_date, erp)

        if top_products:
            fig = create_horizontal_bar_chart(
                data=top_products,
                x_field='total_revenue',
                y_field='product_name',
                title='',
                x_label=f'Revenue ({settings.CURRENCY_SYMBOL})',
                y_label='Product',
                color='#AB63FA'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No product data available")

    with col2:
        st.markdown("#### 🔄 Odoo vs Focus Comparison")

        if erp_filter == "All":
            comparison = analytics.get_erp_comparison()

            if comparison and len(comparison) > 0:
                # Prepare data for pie chart
                erp_data = []
                for erp_name, metrics in comparison.items():
                    erp_data.append({
                        'erp': erp_name,
                        'revenue': metrics['revenue']
                    })

                fig = create_pie_chart(
                    data=erp_data,
                    names_field='erp',
                    values_field='revenue',
                    title='',
                    colors=['#636EFA', '#EF553B']
                )
                st.plotly_chart(fig, use_container_width=True)

                # Show detailed comparison
                with st.expander("📋 Detailed Comparison"):
                    for erp_name, metrics in comparison.items():
                        st.markdown(f"**{erp_name}:**")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Revenue", format_currency(metrics['revenue'], settings.CURRENCY_SYMBOL))
                        with col_b:
                            st.metric("Invoices", f"{metrics['invoices']:,}")
                        with col_c:
                            st.metric("Customers", f"{metrics['customers']:,}")
                        st.markdown("---")

            else:
                st.info("No data available for comparison")
        else:
            st.info(f"Comparison not available when filtering by {erp_filter}. Select 'All' to see comparison.")

    st.markdown("---")

    # Additional Analytics
    tab1, tab2, tab3 = st.tabs(["📊 Customer Insights", "📦 Product Insights", "📅 Time Analysis"])

    with tab1:
        st.markdown("### Customer Insights")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 💤 Inactive Customers")
            st.caption("Customers with no orders in the last 90 days")

            inactive_customers = analytics.get_inactive_customers(90, erp)

            if inactive_customers:
                st.dataframe(
                    inactive_customers,
                    use_container_width=True,
                    hide_index=True,
                    height=300
                )
                st.caption(f"Total: {len(inactive_customers)} inactive customers")
            else:
                st.success("All customers are active!")

        with col2:
            st.markdown("#### 🔍 Customer Search")

            # Get all customers for search
            all_customers = analytics.get_top_customers(1000, start_date, end_date, erp)

            if all_customers:
                customer_names = [c['customer_name'] for c in all_customers]
                selected_customer = st.selectbox(
                    "Select a customer to view details",
                    options=[""] + customer_names
                )

                if selected_customer:
                    customer_details = analytics.get_customer_purchase_history(selected_customer, erp)

                    if customer_details:
                        summary = customer_details['summary']

                        st.markdown(f"**Customer:** {summary['customer_name']}")

                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Total Spent", format_currency(summary['total_spent'], settings.CURRENCY_SYMBOL))
                            st.metric("First Purchase", summary['first_purchase'] or 'N/A')
                        with col_b:
                            st.metric("Total Sales", f"{summary['total_sales']:,}")
                            st.metric("Last Purchase", summary['last_purchase'] or 'N/A')

                        st.markdown("**Recent Sales:**")
                        sales = customer_details['sales'][:10]
                        st.dataframe(sales, use_container_width=True, hide_index=True)
                    else:
                        st.warning("No data found for this customer")
            else:
                st.info("No customer data available")

    with tab2:
        st.markdown("### Product Insights")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📦 All Products Performance")

            all_products = analytics.get_top_products(50, start_date, end_date, erp)

            if all_products:
                st.dataframe(
                    all_products,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
                st.caption(f"Showing top {len(all_products)} products")
            else:
                st.info("No product data available")

        with col2:
            st.markdown("#### 📊 Product Statistics")

            if all_products:
                total_products = len(all_products)
                total_quantity = sum(p['total_quantity'] for p in all_products if p['total_quantity'])
                total_product_revenue = sum(p['total_revenue'] for p in all_products if p['total_revenue'])

                st.metric("Total Products", f"{total_products:,}")
                st.metric("Total Units Sold", f"{total_quantity:,.0f}")
                st.metric("Total Revenue", format_currency(total_product_revenue, settings.CURRENCY_SYMBOL))

                # Top product
                if all_products:
                    top_product = all_products[0]
                    st.markdown("**🏆 Top Product:**")
                    st.markdown(f"- **Name:** {top_product['product_name']}")
                    st.markdown(f"- **Revenue:** {format_currency(top_product['total_revenue'], settings.CURRENCY_SYMBOL)}")
                    st.markdown(f"- **Units Sold:** {top_product['total_quantity']:,.0f}")
            else:
                st.info("No product statistics available")

    with tab3:
        st.markdown("### Time Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📅 Sales by Day of Week")

            day_data = analytics.get_sales_by_day_of_week(erp)

            if day_data:
                fig = create_bar_chart(
                    data=day_data,
                    x_field='day_of_week',
                    y_field='revenue',
                    title='',
                    x_label='Day of Week',
                    y_label=f'Revenue ({settings.CURRENCY_SYMBOL})',
                    color='#FFA15A'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available")

        with col2:
            st.markdown("#### 📊 Monthly Statistics")

            monthly_data = analytics.get_revenue_by_month(12, erp)

            if monthly_data:
                st.dataframe(
                    monthly_data,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
            else:
                st.info("No monthly data available")

    # Export Options
    st.markdown("---")

    st.markdown("### 💾 Export Data")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📥 Export Top Customers CSV", use_container_width=True):
            import pandas as pd
            customers_df = pd.DataFrame(analytics.get_top_customers(100, start_date, end_date, erp))
            csv = customers_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="top_customers.csv",
                mime="text/csv"
            )

    with col2:
        if st.button("📥 Export Top Products CSV", use_container_width=True):
            import pandas as pd
            products_df = pd.DataFrame(analytics.get_top_products(100, start_date, end_date, erp))
            csv = products_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="top_products.csv",
                mime="text/csv"
            )

    with col3:
        if st.button("📥 Export Revenue Trend CSV", use_container_width=True):
            import pandas as pd
            revenue_df = pd.DataFrame(analytics.get_revenue_by_month(12, erp))
            csv = revenue_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="revenue_trend.csv",
                mime="text/csv"
            )


if __name__ == "__main__":
    main()
