-- Sales & Quotation Chatbot Database Schema (SQLite)

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL UNIQUE,
    item_group TEXT,
    item_code TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales/Invoices table
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    invoice_date DATE,
    due_date DATE,
    customer_po_date DATE,
    voucher_no TEXT,
    customer_po_no TEXT,
    excise_inv_no TEXT,
    account_code TEXT,
    payment_terms TEXT,
    rma TEXT,
    batch_number TEXT,
    quantity DECIMAL(10, 2),
    selling_rate DECIMAL(10, 2),
    selling_gross DECIMAL(10, 2),
    discount_percent DECIMAL(5, 2),
    net_rate DECIMAL(10, 2),
    discount_percent_2 DECIMAL(5, 2),
    net_gross DECIMAL(10, 2),
    packing_forwarding DECIMAL(10, 2),
    freight DECIMAL(10, 2),
    insurance DECIMAL(10, 2),
    assessable_value DECIMAL(10, 2),
    cgst DECIMAL(10, 2),
    sgst DECIMAL(10, 2),
    igst DECIMAL(10, 2),
    total_amount DECIMAL(10, 2) NOT NULL,
    engineer TEXT,
    transporter TEXT,
    units TEXT,
    freight_term TEXT,
    tax_master TEXT,
    form_type TEXT,
    links TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Quotations table
CREATE TABLE IF NOT EXISTS quotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    creation_date TIMESTAMP,
    order_reference TEXT,
    status TEXT,
    salesperson TEXT,
    product_name TEXT,
    quantity DECIMAL(10, 2),
    unit_price DECIMAL(10, 2),
    discount_percent DECIMAL(5, 2),
    untaxed_amount DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

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
