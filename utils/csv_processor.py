"""
CSV Processor for Sales Data
Handles CSV upload, validation, normalization, and ETL operations.
"""

import pandas as pd
import io
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import re


class CSVProcessor:
    """Process and validate CSV files for sales data import."""

    # Common column name variations (mapped to standard names)
    COLUMN_MAPPINGS = {
        'customer_name': ['customer name', 'customer', 'client', 'client name', 'buyer'],
        'product_name': ['product name', 'product', 'product delivered', 'item', 'item name'],
        'unit_price': ['unit price', 'price', 'rate', 'unit rate', 'price per unit'],
        'quantity': ['quantity', 'qty', 'amount', 'units'],
        'total_amount': ['total invoice', 'total amount', 'total', 'invoice total', 'amount'],
        'invoice_date': ['invoice date', 'date', 'order date', 'sale date'],
        'invoice_number': ['invoice number', 'invoice no', 'invoice #', 'inv no', 'invoice_no']
    }

    def __init__(self):
        """Initialize CSV processor."""
        self.df: Optional[pd.DataFrame] = None
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def read_csv(self, file_content: Any, file_extension: str = '.csv') -> bool:
        """Read CSV or Excel file into DataFrame.

        Args:
            file_content: File content (bytes or file-like object)
            file_extension: File extension (.csv, .xlsx, .xls)

        Returns:
            True if successful, False otherwise
        """
        try:
            if file_extension == '.csv':
                self.df = pd.read_csv(file_content, encoding='utf-8')
            elif file_extension in ['.xlsx', '.xls']:
                self.df = pd.read_excel(file_content)
            else:
                self.errors.append(f"Unsupported file format: {file_extension}")
                return False

            return True
        except Exception as e:
            self.errors.append(f"Error reading file: {str(e)}")
            return False

    def normalize_column_names(self) -> None:
        """Normalize column names to standard format."""
        if self.df is None:
            return

        # Convert all column names to lowercase and strip whitespace
        self.df.columns = self.df.columns.str.lower().str.strip()

        # Map variations to standard names
        column_mapping = {}
        for standard_name, variations in self.COLUMN_MAPPINGS.items():
            for col in self.df.columns:
                if col in variations:
                    column_mapping[col] = standard_name
                    break

        if column_mapping:
            self.df.rename(columns=column_mapping, inplace=True)

    def validate_required_columns(self) -> bool:
        """Validate that required columns are present.

        Returns:
            True if valid, False otherwise
        """
        if self.df is None:
            self.errors.append("No data loaded")
            return False

        required_columns = ['customer_name', 'product_name', 'total_amount']

        missing_columns = [col for col in required_columns if col not in self.df.columns]

        if missing_columns:
            self.errors.append(f"Missing required columns: {', '.join(missing_columns)}")
            self.errors.append(f"Found columns: {', '.join(self.df.columns)}")
            return False

        return True

    def clean_data(self) -> None:
        """Clean and normalize data."""
        if self.df is None:
            return

        # Remove completely empty rows
        self.df.dropna(how='all', inplace=True)

        # Clean customer names
        if 'customer_name' in self.df.columns:
            self.df['customer_name'] = self.df['customer_name'].astype(str).str.strip()
            self.df = self.df[self.df['customer_name'] != '']
            self.df = self.df[self.df['customer_name'] != 'nan']

        # Clean product names
        if 'product_name' in self.df.columns:
            self.df['product_name'] = self.df['product_name'].astype(str).str.strip()
            self.df = self.df[self.df['product_name'] != '']
            self.df = self.df[self.df['product_name'] != 'nan']

        # Clean and convert numeric fields
        numeric_fields = ['unit_price', 'quantity', 'total_amount']
        for field in numeric_fields:
            if field in self.df.columns:
                # Remove currency symbols and commas
                self.df[field] = self.df[field].astype(str).str.replace('[\$,₹€£]', '', regex=True)
                self.df[field] = pd.to_numeric(self.df[field], errors='coerce')

        # Clean invoice numbers
        if 'invoice_number' in self.df.columns:
            self.df['invoice_number'] = self.df['invoice_number'].astype(str).str.strip()
            self.df.loc[self.df['invoice_number'] == 'nan', 'invoice_number'] = None

        # Parse dates
        if 'invoice_date' in self.df.columns:
            self.df['invoice_date'] = pd.to_datetime(self.df['invoice_date'], errors='coerce')
            # Convert to string format for database
            self.df['invoice_date'] = self.df['invoice_date'].dt.strftime('%Y-%m-%d')

    def calculate_missing_values(self) -> None:
        """Calculate missing values based on available data."""
        if self.df is None:
            return

        # If total_amount is missing but we have unit_price and quantity
        if 'total_amount' in self.df.columns and 'unit_price' in self.df.columns and 'quantity' in self.df.columns:
            mask = self.df['total_amount'].isna() & self.df['unit_price'].notna() & self.df['quantity'].notna()
            self.df.loc[mask, 'total_amount'] = self.df.loc[mask, 'unit_price'] * self.df.loc[mask, 'quantity']

        # If quantity is missing but we have total_amount and unit_price
        if 'quantity' in self.df.columns and 'unit_price' in self.df.columns and 'total_amount' in self.df.columns:
            mask = self.df['quantity'].isna() & self.df['unit_price'].notna() & self.df['total_amount'].notna()
            mask = mask & (self.df['unit_price'] != 0)
            self.df.loc[mask, 'quantity'] = self.df.loc[mask, 'total_amount'] / self.df.loc[mask, 'unit_price']

        # If unit_price is missing but we have total_amount and quantity
        if 'unit_price' in self.df.columns and 'quantity' in self.df.columns and 'total_amount' in self.df.columns:
            mask = self.df['unit_price'].isna() & self.df['quantity'].notna() & self.df['total_amount'].notna()
            mask = mask & (self.df['quantity'] != 0)
            self.df.loc[mask, 'unit_price'] = self.df.loc[mask, 'total_amount'] / self.df.loc[mask, 'quantity']

        # Set default quantity to 1 if still missing
        if 'quantity' in self.df.columns:
            self.df['quantity'].fillna(1.0, inplace=True)

        # Calculate unit_price if still missing and total is available
        if 'unit_price' in self.df.columns and 'total_amount' in self.df.columns:
            mask = self.df['unit_price'].isna() & self.df['total_amount'].notna()
            self.df.loc[mask, 'unit_price'] = self.df.loc[mask, 'total_amount']

    def validate_data(self) -> bool:
        """Validate cleaned data.

        Returns:
            True if valid, False otherwise
        """
        if self.df is None or len(self.df) == 0:
            self.errors.append("No valid data rows found after cleaning")
            return False

        # Check for null values in required fields
        null_customers = self.df['customer_name'].isna().sum()
        null_products = self.df['product_name'].isna().sum()
        null_totals = self.df['total_amount'].isna().sum()

        if null_customers > 0:
            self.warnings.append(f"{null_customers} rows with missing customer names will be skipped")
            self.df = self.df[self.df['customer_name'].notna()]

        if null_products > 0:
            self.warnings.append(f"{null_products} rows with missing product names will be skipped")
            self.df = self.df[self.df['product_name'].notna()]

        if null_totals > 0:
            self.warnings.append(f"{null_totals} rows with missing total amounts will be skipped")
            self.df = self.df[self.df['total_amount'].notna()]

        # Check for negative amounts
        if 'total_amount' in self.df.columns:
            negative_amounts = (self.df['total_amount'] < 0).sum()
            if negative_amounts > 0:
                self.warnings.append(f"{negative_amounts} rows with negative amounts found")

        return len(self.df) > 0

    def get_preview(self, n: int = 10) -> pd.DataFrame:
        """Get preview of processed data.

        Args:
            n: Number of rows to preview

        Returns:
            Preview DataFrame
        """
        if self.df is None:
            return pd.DataFrame()
        return self.df.head(n)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the data.

        Returns:
            Dictionary with summary statistics
        """
        if self.df is None:
            return {}

        summary = {
            'total_rows': len(self.df),
            'unique_customers': self.df['customer_name'].nunique() if 'customer_name' in self.df.columns else 0,
            'unique_products': self.df['product_name'].nunique() if 'product_name' in self.df.columns else 0,
            'total_revenue': self.df['total_amount'].sum() if 'total_amount' in self.df.columns else 0,
            'date_range': None
        }

        if 'invoice_date' in self.df.columns:
            valid_dates = pd.to_datetime(self.df['invoice_date'], errors='coerce')
            if valid_dates.notna().any():
                summary['date_range'] = f"{valid_dates.min()} to {valid_dates.max()}"

        return summary

    def process_file(self, file_content: Any, file_extension: str = '.csv') -> Tuple[bool, Dict[str, Any]]:
        """Main processing pipeline for CSV file.

        Args:
            file_content: File content
            file_extension: File extension

        Returns:
            Tuple of (success, summary_dict)
        """
        self.errors = []
        self.warnings = []

        # Step 1: Read file
        if not self.read_csv(file_content, file_extension):
            return False, {'errors': self.errors}

        # Step 2: Normalize column names
        self.normalize_column_names()

        # Step 3: Validate required columns
        if not self.validate_required_columns():
            return False, {'errors': self.errors}

        # Step 4: Clean data
        self.clean_data()

        # Step 5: Calculate missing values
        self.calculate_missing_values()

        # Step 6: Validate data
        if not self.validate_data():
            return False, {'errors': self.errors, 'warnings': self.warnings}

        # Step 7: Get summary
        summary = self.get_summary()
        summary['warnings'] = self.warnings

        return True, summary

    def get_processed_data(self) -> Optional[pd.DataFrame]:
        """Get processed DataFrame.

        Returns:
            Processed DataFrame or None
        """
        return self.df
