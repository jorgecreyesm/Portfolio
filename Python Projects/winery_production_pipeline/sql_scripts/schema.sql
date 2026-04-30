-- 1. Create Suppliers Table
CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(255) UNIQUE NOT NULL
);

-- 2. Create Item Types Table
CREATE TABLE item_types (
    type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(100) UNIQUE NOT NULL
);

-- 3. Create Items Table
CREATE TABLE items (
    item_code VARCHAR(50) PRIMARY KEY,
    item_description TEXT NOT NULL,
    type_id INTEGER REFERENCES item_types(type_id),
    supplier_id INTEGER REFERENCES suppliers(supplier_id)
);

-- 4. Create Monthly Sales Table (The Fact Table)
CREATE TABLE monthly_sales (
    sales_id SERIAL PRIMARY KEY,
    item_code VARCHAR(50) REFERENCES items(item_code),
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    retail_sales NUMERIC(12, 2),
    retail_transfers NUMERIC(12, 2),
    warehouse_sales NUMERIC(12, 2)
);