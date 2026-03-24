"""
Upload Data Page v2
Handles Sales and Quotation data uploads (no Odoo/Focus distinction).
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from database.db_manager import get_db_manager
from auth.auth_manager import require_auth


st.set_page_config(
    page_title="Upload Data - Sales Chatbot",
    page_icon="📤",
    layout="wide"
)


def process_sales_data(file_content, file_extension):
    """Process and import sales data.

    Args:
        file_content: Uploaded file content
        file_extension: File extension

    Returns:
        Dictionary with import statistics
    """
    try:
        # Read Excel with header at row 5
        df = pd.read_excel(file_content, header=5)

        # Clean data
        df = df.dropna(subset=['Customer Name', 'Item', 'Total'], how='all')
        df = df[df['Customer Name'].notna() & df['Item'].notna() & df['Total'].notna()]
        df = df[df['Total'] > 0]

        db = get_db_manager()

        stats = {
            'customers_added': set(),
            'products_added': set(),
            'sales_added': 0,
            'errors': []
        }

        for idx, row in df.iterrows():
            try:
                # Customer
                customer_id = db.upsert_customer(
                    customer_name=str(row.get('Customer Name', '')).strip(),
                    gst_no=str(row.get('GST No', '')) if pd.notna(row.get('GST No')) else None,
                    branch=str(row.get('Branch', '')) if pd.notna(row.get('Branch')) else None,
                    state=str(row.get('State', '')) if pd.notna(row.get('State')) else None,
                    city=str(row.get('City', '')) if pd.notna(row.get('City')) else None,
                    mobile_no=str(row.get('Mobile No', '')) if pd.notna(row.get('Mobile No')) else None,
                    email_id=str(row.get('Email Id', '')) if pd.notna(row.get('Email Id')) else None
                )
                stats['customers_added'].add(customer_id)

                # Product
                product_id = db.upsert_product(
                    item_name=str(row.get('Item', '')).strip(),
                    item_group=str(row.get('Item Group', '')) if pd.notna(row.get('Item Group')) else None,
                    item_code=str(row.get('ItemCode', '')) if pd.notna(row.get('ItemCode')) else None
                )
                stats['products_added'].add(product_id)

                # Dates
                invoice_date = pd.to_datetime(row.get('Date'), errors='coerce')
                invoice_date = invoice_date.strftime('%Y-%m-%d') if pd.notna(invoice_date) else None

                due_date = pd.to_datetime(row.get('Due Date'), errors='coerce')
                due_date = due_date.strftime('%Y-%m-%d') if pd.notna(due_date) else None

                po_date = pd.to_datetime(row.get('Customer PO Date'), errors='coerce')
                po_date = po_date.strftime('%Y-%m-%d') if pd.notna(po_date) else None

                # Sale data
                sale_data = {
                    'customer_id': customer_id,
                    'product_id': product_id,
                    'invoice_date': invoice_date,
                    'due_date': due_date,
                    'customer_po_date': po_date,
                    'voucher_no': str(row.get('Voucher No', '')) if pd.notna(row.get('Voucher No')) else None,
                    'customer_po_no': str(row.get('Customer PO No', '')) if pd.notna(row.get('Customer PO No')) else None,
                    'payment_terms': str(row.get('Payment Terms', '')) if pd.notna(row.get('Payment Terms')) else None,
                    'rma': str(row.get('RMA', '')) if pd.notna(row.get('RMA')) else None,
                    'quantity': float(row.get('Quantity', 0)) if pd.notna(row.get('Quantity')) else None,
                    'selling_rate': float(row.get('Selling Rate', 0)) if pd.notna(row.get('Selling Rate')) else None,
                    'selling_gross': float(row.get('Selling Gross', 0)) if pd.notna(row.get('Selling Gross')) else None,
                    'net_rate': float(row.get('Rate', 0)) if pd.notna(row.get('Rate')) else None,
                    'net_gross': float(row.get('Gross', 0)) if pd.notna(row.get('Gross')) else None,
                    'total_amount': float(row.get('Total', 0)),
                }

                db.insert_sale(sale_data)
                stats['sales_added'] += 1

            except Exception as e:
                stats['errors'].append(f"Row {idx + 1}: {str(e)}")

        return {
            'success': True,
            'customers': len(stats['customers_added']),
            'products': len(stats['products_added']),
            'records': stats['sales_added'],
            'errors': stats['errors']
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def process_quotation_data(file_content, file_extension):
    """Process and import quotation data.

    Args:
        file_content: Uploaded file content
        file_extension: File extension

    Returns:
        Dictionary with import statistics
    """
    try:
        # Read Excel (header at row 0 for quotations)
        df = pd.read_excel(file_content, header=0)

        # Clean data
        df = df.dropna(subset=['Customer'], how='all')
        df = df[df['Customer'].notna()]

        db = get_db_manager()

        stats = {
            'customers_added': set(),
            'quotations_added': 0,
            'errors': []
        }

        for idx, row in df.iterrows():
            try:
                # Customer
                customer_name = str(row.get('Customer', '')).strip()
                if not customer_name:
                    continue

                customer_id = db.upsert_customer(customer_name=customer_name)
                stats['customers_added'].add(customer_id)

                # Date
                creation_date = pd.to_datetime(row.get('Creation Date'), errors='coerce')
                creation_date = creation_date.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(creation_date) else None

                # Quotation data
                quotation_data = {
                    'customer_id': customer_id,
                    'creation_date': creation_date,
                    'order_reference': str(row.get('Order Reference', '')) if pd.notna(row.get('Order Reference')) else None,
                    'status': str(row.get('Status', '')) if pd.notna(row.get('Status')) else None,
                    'salesperson': str(row.get('Salesperson', '')) if pd.notna(row.get('Salesperson')) else None,
                    'product_name': str(row.get('Order Lines/Display Name', '')) if pd.notna(row.get('Order Lines/Display Name')) else None,
                    'quantity': float(row.get('Order Lines/Quantity', 0)) if pd.notna(row.get('Order Lines/Quantity')) else None,
                    'unit_price': float(row.get('Order Lines/Unit Price', 0)) if pd.notna(row.get('Order Lines/Unit Price')) else None,
                    'discount_percent': float(row.get('Order Lines/Discount (%)', 0)) if pd.notna(row.get('Order Lines/Discount (%)')) else None,
                    'untaxed_amount': float(row.get('Untaxed Amount', 0)) if pd.notna(row.get('Untaxed Amount')) else None,
                }

                db.insert_quotation(quotation_data)
                stats['quotations_added'] += 1

            except Exception as e:
                stats['errors'].append(f"Row {idx + 1}: {str(e)}")

        return {
            'success': True,
            'customers': len(stats['customers_added']),
            'records': stats['quotations_added'],
            'errors': stats['errors']
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def main():
    """Main upload page logic."""
    require_auth()
    st.title("📤 Upload Data")

    st.markdown("""
    Upload your sales data or quotation data. The system will automatically process and store it.
    """)

    st.markdown("---")

    # Data Type Selection
    col1, col2 = st.columns([1, 3])

    with col1:
        data_type = st.radio(
            "Select Data Type",
            options=["Sales Data", "Quotation Data"],
            help="Choose whether you're uploading sales/invoices or quotations"
        )

    with col2:
        if data_type == "Sales Data":
            st.info("""
            📊 **Sales Data** - Upload your sales ledger/invoice data
            - Expected columns: Date, Customer Name, Item, Total, Payment Terms, etc.
            - Header should be at row 6 in Excel
            """)
        else:
            st.info("""
            📋 **Quotation Data** - Upload your quotation/sale order data
            - Expected columns: Creation Date, Customer, Order Lines, Status, etc.
            - Header should be at row 1 in Excel
            """)

    st.markdown("---")

    # File Upload
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload your Excel file"
    )

    if uploaded_file is not None:
        file_extension = Path(uploaded_file.name).suffix.lower()

        st.success(f"✅ File uploaded: {uploaded_file.name}")

        # Show preview button
        if st.button("👀 Preview Data", use_container_width=True):
            with st.spinner("Loading preview..."):
                try:
                    if data_type == "Sales Data":
                        df_preview = pd.read_excel(uploaded_file, header=5, nrows=10)
                    else:
                        df_preview = pd.read_excel(uploaded_file, header=0, nrows=10)

                    st.markdown("### Data Preview")
                    st.dataframe(df_preview, use_container_width=True, hide_index=True)

                except Exception as e:
                    st.error(f"Error loading preview: {e}")

        st.markdown("---")

        # Import Button
        st.markdown(f"### 💾 Import {data_type}")

        if st.button(f"🚀 Import {data_type}", type="primary", use_container_width=True):
            with st.spinner(f"Importing {data_type.lower()}..."):
                # Reset file pointer
                uploaded_file.seek(0)

                if data_type == "Sales Data":
                    result = process_sales_data(uploaded_file, file_extension)
                else:
                    result = process_quotation_data(uploaded_file, file_extension)

                if result['success']:
                    st.success(f"✅ {data_type} imported successfully!")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Customers", f"{result['customers']:,}")
                    with col2:
                        if 'products' in result:
                            st.metric("Products", f"{result['products']:,}")
                    with col3:
                        st.metric("Records", f"{result['records']:,}")

                    if result.get('errors'):
                        with st.expander(f"⚠️ {len(result['errors'])} Errors"):
                            for error in result['errors'][:10]:
                                st.error(error)

                    st.balloons()

                    # Navigation
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💬 Go to Chat →"):
                            st.switch_page("pages/2_💬_Chat.py")
                    with col2:
                        if st.button("📊 Go to Analytics →"):
                            st.switch_page("pages/3_📊_Analytics.py")

                else:
                    st.error("❌ Import failed!")
                    st.error(result.get('error', 'Unknown error'))

    else:
        st.info("👆 Upload a file to get started")


if __name__ == "__main__":
    main()
