SELECT 
    year, 
    month,
    SUM(retail_sales) AS monthly_sales,
    AVG(SUM(retail_sales)) OVER (
        ORDER BY year, month 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS three_month_moving_avg
FROM monthly_sales
GROUP BY year, month
ORDER BY year, month;

WITH SupplierSales AS (
    SELECT 
        s.supplier_name,
        SUM(m.warehouse_sales) as total_warehouse_sales
    FROM monthly_sales m
    JOIN items i ON m.item_code = i.item_code
    JOIN suppliers s ON i.supplier_id = s.supplier_id
    GROUP BY s.supplier_name
),
RankedSales AS (
    SELECT 
        supplier_name,
        total_warehouse_sales,
        SUM(total_warehouse_sales) OVER (ORDER BY total_warehouse_sales DESC) as running_total,
        SUM(total_warehouse_sales) OVER () as grand_total
    FROM SupplierSales
)
SELECT 
    supplier_name,
    total_warehouse_sales,
    ROUND((running_total / grand_total) * 100, 2) as cumulative_market_share_pct
FROM RankedSales
WHERE (running_total / grand_total) <= 0.81 -- Finding the "Top 80%"
ORDER BY total_warehouse_sales DESC;

EXPLAIN ANALYZE 
SELECT * FROM monthly_sales WHERE item_code = '1001';
CREATE INDEX idx_sales_item_code ON monthly_sales(item_code);
CREATE INDEX idx_sales_date ON monthly_sales(year, month);
EXPLAIN ANALYZE SELECT * FROM monthly_sales WHERE item_code = '1001';

-- identifying the top suppliers responsible for 80% of revenue
WITH SupplierSales AS (
    SELECT 
        s.supplier_name,
        SUM(m.retail_sales) as total_retail_sales
    FROM monthly_sales m
    JOIN items i ON m.item_code = i.item_code
    JOIN suppliers s ON i.supplier_id = s.supplier_id
    GROUP BY s.supplier_name
),
RankedSales AS (
    SELECT 
        supplier_name,
        total_retail_sales,
        SUM(total_retail_sales) OVER (ORDER BY total_retail_sales DESC) as running_total,
        SUM(total_retail_sales) OVER () as grand_total
    FROM SupplierSales
)
SELECT 
    supplier_name,
    total_retail_sales,
    ROUND((running_total / grand_total) * 100, 2) as cumulative_market_share_pct
FROM RankedSales
WHERE (running_total / grand_total) <= 0.85 -- Adjusted to see the "Core" group
ORDER BY total_retail_sales DESC;
CREATE INDEX idx_items_supplier_id ON items(supplier_id);