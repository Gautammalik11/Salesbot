-- ============================================================
-- Supabase (PostgreSQL) Schema for Sales Chatbot
-- Run this ONCE in Supabase SQL Editor
-- ============================================================

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    customer_name TEXT NOT NULL UNIQUE,
    gst_no TEXT,
    branch TEXT,
    state TEXT,
    city TEXT,
    mobile_no TEXT,
    email_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    item_name TEXT NOT NULL UNIQUE,
    item_group TEXT,
    item_code TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales / Invoices table
CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,

    -- Date fields
    invoice_date DATE,
    due_date DATE,
    customer_po_date DATE,

    -- Reference numbers
    voucher_no TEXT,
    customer_po_no TEXT,
    excise_inv_no TEXT,
    account_code TEXT,

    -- Payment & terms
    payment_terms TEXT,

    -- Product details
    rma TEXT,
    batch_number TEXT,

    -- Quantities & rates
    quantity DECIMAL(15, 4),
    selling_rate DECIMAL(15, 4),
    selling_gross DECIMAL(15, 4),
    discount_percent DECIMAL(8, 4),
    net_rate DECIMAL(15, 4),
    discount_percent_2 DECIMAL(8, 4),
    net_gross DECIMAL(15, 4),

    -- Charges
    packing_forwarding DECIMAL(15, 4),
    freight DECIMAL(15, 4),
    insurance DECIMAL(15, 4),
    assessable_value DECIMAL(15, 4),

    -- Taxes (GST era - 2017 onwards)
    cgst DECIMAL(15, 4),
    sgst DECIMAL(15, 4),
    igst DECIMAL(15, 4),

    -- Total
    total_amount DECIMAL(15, 4) NOT NULL,

    -- Additional info
    engineer TEXT,
    transporter TEXT,
    units TEXT,
    freight_term TEXT,
    tax_master TEXT,
    form_type TEXT,
    links TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quotations table
CREATE TABLE IF NOT EXISTS quotations (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,

    creation_date TIMESTAMP,
    order_reference TEXT,
    status TEXT,
    salesperson TEXT,

    product_name TEXT,
    quantity DECIMAL(15, 4),
    unit_price DECIMAL(15, 4),
    discount_percent DECIMAL(8, 4),
    untaxed_amount DECIMAL(15, 4),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_customer_name ON customers(customer_name);
CREATE INDEX IF NOT EXISTS idx_customer_gst ON customers(gst_no);

CREATE INDEX IF NOT EXISTS idx_product_name ON products(item_name);
CREATE INDEX IF NOT EXISTS idx_product_code ON products(item_code);

CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(invoice_date);
CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_voucher ON sales(voucher_no);

CREATE INDEX IF NOT EXISTS idx_quot_date ON quotations(creation_date);
CREATE INDEX IF NOT EXISTS idx_quot_customer ON quotations(customer_id);
CREATE INDEX IF NOT EXISTS idx_quot_status ON quotations(status);
