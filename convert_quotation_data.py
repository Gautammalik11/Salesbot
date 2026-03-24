#!/usr/bin/env python3
"""
Convert Quotation/Sale Order Data to Database
Handles quotation Excel files with all columns.
"""

import pandas as pd
import sys
from pathlib import Path
from database.db_manager import get_db_manager


def convert_and_import_quotations(input_file):
    """Convert quotation Excel and import directly to database.

    Args:
        input_file: Path to input Excel file
    """
    print(f"📂 Reading quotation file: {input_file}")

    # Read Excel file (quotations have header at row 0)
    df = pd.read_excel(input_file, header=0)

    print(f"✅ Found {len(df)} rows")
    print(f"Columns: {list(df.columns)}")

    # Clean data - remove empty rows
    df = df.dropna(subset=['Customer'], how='all')
    df = df[df['Customer'].notna()]

    print(f"🧹 Cleaned to {len(df)} valid rows")

    # Initialize database
    db = get_db_manager()

    stats = {
        'customers_added': set(),
        'quotations_added': 0,
        'errors': []
    }

    print(f"\n💾 Importing to database...")

    for idx, row in df.iterrows():
        try:
            # Get or create customer
            customer_name = str(row.get('Customer', '')).strip()
            if not customer_name:
                continue

            customer_id = db.upsert_customer(customer_name=customer_name)
            stats['customers_added'].add(customer_id)

            # Prepare creation date
            creation_date = pd.to_datetime(row.get('Creation Date'), errors='coerce')
            creation_date = creation_date.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(creation_date) else None

            # Prepare quotation data
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

            # Insert quotation
            db.insert_quotation(quotation_data)
            stats['quotations_added'] += 1

            if (idx + 1) % 50 == 0:
                print(f"  Processed {idx + 1} rows...")

        except Exception as e:
            stats['errors'].append(f"Row {idx + 1}: {str(e)}")

    print(f"\n✅ Import complete!")
    print(f"\n📈 Statistics:")
    print(f"  • Customers: {len(stats['customers_added']):,}")
    print(f"  • Quotations: {stats['quotations_added']:,}")

    if stats['errors']:
        print(f"\n⚠️  Errors: {len(stats['errors'])}")
        for error in stats['errors'][:5]:
            print(f"    {error}")

    return stats


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_quotation_data.py <quotation_excel_file>")
        print("\nExample:")
        print("  python convert_quotation_data.py ~/Downloads/Sale\\ Order\\ \\(sale.order\\).xlsx")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        convert_and_import_quotations(input_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
