"""
Sales Data Chatbot Platform
Main Streamlit application entry point.
"""

import streamlit as st
import os
from pathlib import Path
from database.db_manager import get_db_manager
from config.settings import settings
from auth.auth_manager import require_auth, get_auth_manager


# Page configuration
st.set_page_config(
    page_title=settings.APP_TITLE,
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables."""
    if 'db_initialized' not in st.session_state:
        st.session_state.db_initialized = False

    if 'api_key_validated' not in st.session_state:
        st.session_state.api_key_validated = False


def initialize_database():
    """Initialize database if not already done."""
    if not st.session_state.db_initialized:
        try:
            db = get_db_manager()
            db.init_database()
            st.session_state.db_initialized = True
            return True
        except Exception as e:
            st.error(f"Database initialization failed: {e}")
            return False
    return True


def validate_api_key():
    """Validate Anthropic API key."""
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "your_api_key_here":
        return False
    return True


def show_sidebar():
    """Display sidebar with app information and settings."""
    with st.sidebar:
        st.title("💬 Sales Chatbot")

        # User info + logout
        user_name = st.session_state.get('user_name', 'User')
        user_role = st.session_state.get('user_role', '')
        st.markdown(f"👤 **{user_name}** `{user_role}`")
        if st.button("🚪 Logout", use_container_width=True):
            get_auth_manager().logout()
            st.rerun()

        st.markdown("---")

        # API Key status
        st.subheader("⚙️ Configuration")

        if validate_api_key():
            st.success("✅ API Key Configured")
        else:
            st.error("❌ API Key Not Configured")
            st.info("Please add your Anthropic API key to the `.env` file")

        st.markdown("---")

        # Database stats
        st.subheader("📊 Database Stats")

        if st.session_state.db_initialized:
            try:
                db = get_db_manager()
                stats = db.get_table_stats()

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Customers", f"{stats.get('customers', 0):,}")
                    st.metric("Products", f"{stats.get('products', 0):,}")
                with col2:
                    st.metric("Invoices", f"{stats.get('invoices', 0):,}")
                    st.metric("Line Items", f"{stats.get('invoice_items', 0):,}")

            except Exception as e:
                st.error(f"Error loading stats: {e}")
        else:
            st.info("Database not initialized")

        st.markdown("---")

        # Navigation help
        st.subheader("📖 Quick Start")
        st.markdown("""
        1. **Upload Data**: Import your CSV files
        2. **Chat**: Ask questions about your data
        3. **Analytics**: View insights and reports
        """)

        st.markdown("---")

        # About
        st.subheader("ℹ️ About")
        st.markdown("""
        Sales Data Chatbot Platform helps you analyze sales data from Odoo and Focus ERPs using AI-powered natural language queries.

        **Tech Stack:**
        - Streamlit
        - SQLite
        - Claude AI
        - LangChain
        - Plotly
        """)

        # Footer
        st.markdown("---")
        st.caption("Built with ❤️ using Streamlit and Claude")


def main():
    """Main application logic."""
    # Initialize session state
    init_session_state()

    # Require login before showing anything
    require_auth()

    # Show sidebar
    show_sidebar()

    # Main content
    st.title("🏠 Welcome to Sales Data Chatbot")

    # Initialize database
    if not st.session_state.db_initialized:
        with st.spinner("Initializing database..."):
            if initialize_database():
                st.success("✅ Database initialized successfully!")
            else:
                st.error("❌ Failed to initialize database. Please check the logs.")
                st.stop()

    # Check API key configuration
    if not validate_api_key():
        st.warning("⚠️ Anthropic API key not configured!")

        st.markdown("""
        ### Setup Instructions

        1. Get your API key from [Anthropic Console](https://console.anthropic.com/)
        2. Create a `.env` file in the project root (copy from `.env.example`)
        3. Add your API key:
           ```
           ANTHROPIC_API_KEY=sk-ant-your-key-here
           ```
        4. Restart the application

        **Note:** Without an API key, the chat functionality will not work.
        """)

        st.info("You can still upload data and view analytics without the API key.")

    else:
        st.success("✅ System ready! Use the sidebar to navigate between pages.")

    # Introduction
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📤 Upload Data")
        st.markdown("""
        Import your sales data from CSV files exported from Odoo and Focus ERPs.

        - Support for CSV and Excel files
        - Automatic data validation
        - Duplicate handling
        - Data preview before import
        """)
        if st.button("Go to Upload →", key="btn_upload"):
            st.switch_page("pages/1_📤_Upload_Data.py")

    with col2:
        st.markdown("### 💬 Chat Interface")
        st.markdown("""
        Ask questions about your sales data in natural language.

        - AI-powered SQL generation
        - Interactive results
        - Query history
        - Example questions provided
        """)
        if st.button("Go to Chat →", key="btn_chat"):
            st.switch_page("pages/2_💬_Chat.py")

    with col3:
        st.markdown("### 📊 Analytics")
        st.markdown("""
        View comprehensive analytics and insights about your sales data.

        - Revenue trends
        - Top customers & products
        - ERP comparison
        - Custom date filters
        """)
        if st.button("Go to Analytics →", key="btn_analytics"):
            st.switch_page("pages/3_📊_Analytics.py")

    st.markdown("---")

    # Sample questions
    st.markdown("### 💡 Example Questions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Revenue & Sales:**
        - What is the total revenue?
        - Show me revenue by month
        - Compare Odoo vs Focus sales

        **Customer Insights:**
        - Who are my top 10 customers?
        - Which customers haven't ordered in 90 days?
        - Show me purchase history for [customer name]
        """)

    with col2:
        st.markdown("""
        **Product Analysis:**
        - What are my best-selling products?
        - Which product generated the most revenue?
        - List all products from Odoo

        **Invoice Details:**
        - Show me all invoices from last month
        - What is the average invoice amount?
        - Show me the highest value invoice
        """)

    st.markdown("---")

    # Getting Started
    with st.expander("🚀 Getting Started Guide"):
        st.markdown("""
        ### Step 1: Upload Your Data

        1. Go to **📤 Upload Data** page
        2. Select your ERP source (Odoo or Focus)
        3. Upload your CSV file
        4. Review the preview
        5. Click "Process Upload"

        ### Step 2: Ask Questions

        1. Go to **💬 Chat** page
        2. Type your question in natural language
        3. View the generated SQL query
        4. See the results in a table

        ### Step 3: Explore Analytics

        1. Go to **📊 Analytics** page
        2. Select date range and filters
        3. View interactive charts and metrics
        4. Export data if needed

        ### CSV Format

        Your CSV should include these columns:
        - Customer Name
        - Product Delivered / Product Name
        - Unit Price
        - Quantity
        - Total Invoice / Total Amount
        - Invoice Date
        - Invoice Number (optional)

        **Example:**
        ```
        Customer Name,Product Delivered,Unit Price,Quantity,Total Invoice,Invoice Date,Invoice Number
        ABC Corp,Widget A,10.00,50,500.00,2024-01-15,INV-001
        XYZ Ltd,Widget B,25.00,20,500.00,2024-01-16,INV-002
        ```
        """)


if __name__ == "__main__":
    main()
