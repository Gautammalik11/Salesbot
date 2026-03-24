-- Sales Data Chatbot Database Schema

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    source_erp TEXT NOT NULL CHECK(source_erp IN ('Odoo', 'Focus')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customer_name, source_erp)
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    source_erp TEXT NOT NULL CHECK(source_erp IN ('Odoo', 'Focus')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_name, source_erp)
);

-- Invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT,
    customer_id INTEGER NOT NULL,
    invoice_date DATE,
    total_amount DECIMAL(10, 2) NOT NULL,
    source_erp TEXT NOT NULL CHECK(source_erp IN ('Odoo', 'Focus')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Invoice line items table
CREATE TABLE IF NOT EXISTS invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity DECIMAL(10, 2),
    unit_price DECIMAL(10, 2),
    line_total DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_customer_name ON customers(customer_name);
CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_source_erp ON invoices(source_erp);
CREATE INDEX IF NOT EXISTS idx_invoice_customer ON invoices(customer_id);
CREATE INDEX IF NOT EXISTS idx_item_invoice ON invoice_items(invoice_id);
CREATE INDEX IF NOT EXISTS idx_item_product ON invoice_items(product_id);
