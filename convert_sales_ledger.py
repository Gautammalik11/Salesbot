#!/usr/bin/env python3
"""
Convert Sales Ledger Excel to App-Compatible Format
Handles accounting software exports (Tally, Focus, etc.)
"""

import pandas as pd
import sys
from pathlib import Path


def convert_sales_ledger(input_file, output_file=None):
    """Convert sales ledger Excel to clean CSV format.

    Args:
        input_file: Path to input Excel file
        output_file: Path to output CSV file (optional)
    """
    print(f"📂 Reading file: {input_file}")

    # Read Excel file with correct header row (row 5)
    df = pd.read_excel(input_file, header=5)

    print(f"✅ Found {len(df)} rows and {len(df.columns)} columns")

    # Map columns to required format
    column_mapping = {
        'Customer Name': 'customer_name',
        'Item': 'product_name',
        'Total': 'total_amount',
        'Date': 'invoice_date',
        'Voucher No': 'invoice_number',
        'Quantity': 'quantity',
        'Rate': 'unit_price'
    }

    # Select and rename columns
    available_cols = [col for col in column_mapping.keys() if col in df.columns]

    print(f"\n📊 Mapping columns:")
    for old, new in column_mapping.items():
        if old in available_cols:
            print(f"  ✓ {old} → {new}")

    # Create new dataframe with mapped columns
    df_clean = df[available_cols].copy()
    df_clean.rename(columns=column_mapping, inplace=True)

    # Clean data
    print(f"\n🧹 Cleaning data...")

    # Remove rows where all key fields are null
    df_clean = df_clean.dropna(subset=['customer_name', 'product_name', 'total_amount'], how='all')

    # Remove empty rows
    df_clean = df_clean.dropna(subset=['customer_name', 'product_name'], how='any')

    # Convert date to proper format
    if 'invoice_date' in df_clean.columns:
        df_clean['invoice_date'] = pd.to_datetime(df_clean['invoice_date'], errors='coerce')
        df_clean['invoice_date'] = df_clean['invoice_date'].dt.strftime('%Y-%m-%d')

    # Ensure numeric columns are numeric
    for col in ['total_amount', 'quantity', 'unit_price']:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

    # Remove rows with null total_amount
    df_clean = df_clean[df_clean['total_amount'].notna()]
    df_clean = df_clean[df_clean['total_amount'] > 0]

    print(f"✅ Cleaned to {len(df_clean)} valid rows")

    # Generate output filename if not provided
    if output_file is None:
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_converted.csv"

    # Save to CSV
    df_clean.to_csv(output_file, index=False)

    print(f"\n💾 Saved to: {output_file}")

    # Show summary
    print(f"\n📈 Summary:")
    print(f"  • Total Rows: {len(df_clean):,}")
    print(f"  • Unique Customers: {df_clean['customer_name'].nunique():,}")
    print(f"  • Unique Products: {df_clean['product_name'].nunique():,}")
    print(f"  • Total Revenue: ₹{df_clean['total_amount'].sum():,.2f}")

    if 'invoice_date' in df_clean.columns:
        date_range = f"{df_clean['invoice_date'].min()} to {df_clean['invoice_date'].max()}"
        print(f"  • Date Range: {date_range}")

    print(f"\n✨ Conversion complete!")
    print(f"📤 You can now upload '{Path(output_file).name}' to the Sales Chatbot app!")

    return output_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_sales_ledger.py <input_excel_file> [output_csv_file]")
        print("\nExample:")
        print("  python convert_sales_ledger.py ~/Downloads/2021.xlsx")
        print("  python convert_sales_ledger.py ~/Downloads/2021.xlsx sales_data.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        convert_sales_ledger(input_file, output_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
