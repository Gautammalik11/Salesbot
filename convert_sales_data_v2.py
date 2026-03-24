#!/usr/bin/env python3
"""
Convert Sales Ledger to Database Format v2
Handles all requested columns including payment terms, GST, RMA, etc.
"""

import pandas as pd
import sys
from pathlib import Path
from database.db_manager import get_db_manager


def convert_and_import_sales(input_file):
    """Convert sales ledger Excel and import directly to database.

    Args:
        input_file: Path to input Excel file
    """
    print(f"📂 Reading sales file: {input_file}")

    # Read Excel file with correct header row (row 5)
    df = pd.read_excel(input_file, header=5)

    print(f"✅ Found {len(df)} rows")

    # Clean data - remove empty rows
    df = df.dropna(subset=['Customer Name', 'Item', 'Total'], how='all')
    df = df[df['Customer Name'].notna() & df['Item'].notna() & df['Total'].notna()]
    df = df[df['Total'] > 0]

    print(f"🧹 Cleaned to {len(df)} valid rows")

    # Initialize database
    db = get_db_manager()

    stats = {
        'customers_added': set(),
        'products_added': set(),
        'sales_added': 0,
        'errors': []
    }

    print(f"\n💾 Importing to database...")

    for idx, row in df.iterrows():
        try:
            # Prepare customer data
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

            # Prepare product data
            product_id = db.upsert_product(
                item_name=str(row.get('Item', '')).strip(),
                item_group=str(row.get('Item Group', '')) if pd.notna(row.get('Item Group')) else None,
                item_code=str(row.get('ItemCode', '')) if pd.notna(row.get('ItemCode')) else None
            )
            stats['products_added'].add(product_id)

            # Prepare dates
            invoice_date = pd.to_datetime(row.get('Date'), errors='coerce')
            invoice_date = invoice_date.strftime('%Y-%m-%d') if pd.notna(invoice_date) else None

            due_date = pd.to_datetime(row.get('Due Date'), errors='coerce')
            due_date = due_date.strftime('%Y-%m-%d') if pd.notna(due_date) else None

            po_date = pd.to_datetime(row.get('Customer PO Date'), errors='coerce')
            po_date = po_date.strftime('%Y-%m-%d') if pd.notna(po_date) else None

            # Prepare sale data with ALL requested columns
            sale_data = {
                'customer_id': customer_id,
                'product_id': product_id,

                # Dates
                'invoice_date': invoice_date,
                'due_date': due_date,
                'customer_po_date': po_date,

                # Reference numbers
                'voucher_no': str(row.get('Voucher No', '')) if pd.notna(row.get('Voucher No')) else None,
                'customer_po_no': str(row.get('Customer PO No', '')) if pd.notna(row.get('Customer PO No')) else None,
                'excise_inv_no': str(row.get('Excise Inv No', '')) if pd.notna(row.get('Excise Inv No')) else None,
                'account_code': str(row.get('AccountCode', '')) if pd.notna(row.get('AccountCode')) else None,

                # Payment & Terms
                'payment_terms': str(row.get('Payment Terms', '')) if pd.notna(row.get('Payment Terms')) else None,

                # Product details
                'rma': str(row.get('RMA', '')) if pd.notna(row.get('RMA')) else None,
                'batch_number': str(row.get('Batch Number', '')) if pd.notna(row.get('Batch Number')) else None,

                # Quantities & Rates (as requested by user)
                'quantity': float(row.get('Quantity', 0)) if pd.notna(row.get('Quantity')) else None,
                'selling_rate': float(row.get('Selling Rate', 0)) if pd.notna(row.get('Selling Rate')) else None,
                'selling_gross': float(row.get('Selling Gross', 0)) if pd.notna(row.get('Selling Gross')) else None,
                'discount_percent': float(row.get('Discount %', 0)) if pd.notna(row.get('Discount %')) else None,
                'net_rate': float(row.get('Rate', 0)) if pd.notna(row.get('Rate')) else None,  # User wants "Rate" as "Net Rate"
                'discount_percent_2': float(row.get('Discount %.1', 0)) if pd.notna(row.get('Discount %.1')) else None,
                'net_gross': float(row.get('Gross', 0)) if pd.notna(row.get('Gross')) else None,  # User wants "Gross" as "Net Gross"

                # Charges
                'packing_forwarding': float(row.get('Packing & Forwardin', 0)) if pd.notna(row.get('Packing & Forwardin')) else None,
                'freight': float(row.get('Freight', 0)) if pd.notna(row.get('Freight')) else None,
                'insurance': float(row.get('Insurance', 0)) if pd.notna(row.get('Insurance')) else None,
                'assessable_value': float(row.get('Assable Value', 0)) if pd.notna(row.get('Assable Value')) else None,

                # Taxes
                'cgst': float(row.get('CGST', 0)) if pd.notna(row.get('CGST')) else None,
                'sgst': float(row.get('SGST', 0)) if pd.notna(row.get('SGST')) else None,
                'igst': float(row.get('IGST', 0)) if pd.notna(row.get('IGST')) else None,

                # Total
                'total_amount': float(row.get('Total', 0)),

                # Additional info
                'engineer': str(row.get('Engineer', '')) if pd.notna(row.get('Engineer')) else None,
                'transporter': str(row.get('Transporter', '')) if pd.notna(row.get('Transporter')) else None,
                'units': str(row.get('Units', '')) if pd.notna(row.get('Units')) else None,
                'freight_term': str(row.get('Freight Term', '')) if pd.notna(row.get('Freight Term')) else None,
                'tax_master': str(row.get('Tax Master', '')) if pd.notna(row.get('Tax Master')) else None,
                'form_type': str(row.get('Form Type', '')) if pd.notna(row.get('Form Type')) else None,
                'links': str(row.get('Links', '')) if pd.notna(row.get('Links')) else None,
            }

            # Insert sale
            db.insert_sale(sale_data)
            stats['sales_added'] += 1

            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1} rows...")

        except Exception as e:
            stats['errors'].append(f"Row {idx + 1}: {str(e)}")

    print(f"\n✅ Import complete!")
    print(f"\n📈 Statistics:")
    print(f"  • Customers: {len(stats['customers_added']):,}")
    print(f"  • Products: {len(stats['products_added']):,}")
    print(f"  • Sales Records: {stats['sales_added']:,}")

    if stats['errors']:
        print(f"\n⚠️  Errors: {len(stats['errors'])}")
        for error in stats['errors'][:5]:
            print(f"    {error}")

    return stats


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_sales_data_v2.py <sales_excel_file>")
        print("\nExample:")
        print("  python convert_sales_data_v2.py ~/Downloads/2021.xlsx")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        convert_and_import_sales(input_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
