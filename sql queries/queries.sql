/*
======================================================
PROJECT: SWIGGY SQL DATA ANALYSIS

Description: Analyzing customer behavior, restaurant performance, 
             and revenue trends using advanced SQL.
======================================================
*/

-- 🔹 1. Customers who never ordered
-- Insight: Inactive users identified for targeted marketing campaigns.
SELECT u.user_id, u.name
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
WHERE o.user_id IS NULL;


-- 🔹 2. Average price per dish
-- Insight: Helps in pricing standardization and competitor benchmarking.
SELECT f.f_name, AVG(m.price) AS avg_price
FROM menu m
JOIN food f ON m.f_id = f.f_id
GROUP BY f.f_name;


-- 🔹 3. Top restaurant (month-wise) - Example for May (Month 5)
-- Insight: Identifies best-performing restaurants for partnerships.
SELECT r.r_name, COUNT(*) AS total_orders
FROM orders o
JOIN restaurants r ON o.r_id = r.r_id
WHERE EXTRACT(MONTH FROM o.date) = 5
GROUP BY r.r_name
ORDER BY total_orders DESC
LIMIT 1;


-- 🔹 4. Restaurants with high sales (> 500)
-- Insight: High revenue restaurants categorized for premium status.
SELECT r.r_name, SUM(o.amount) AS total_sales
FROM orders o
JOIN restaurants r ON o.r_id = r.r_id
GROUP BY r.r_name
HAVING SUM(o.amount) > 500;


-- 🔹 5. Customer orders in specific date range (User ID 1)
-- Insight: Tracks individual user behavior for personalization.
SELECT o.order_id, o.date, f.f_name
FROM orders o
JOIN order_details od ON o.order_id = od.order_id
JOIN food f ON od.f_id = f.f_id
WHERE o.user_id = 1
AND o.date BETWEEN '2022-05-01' AND '2022-06-30';


-- 🔹 6. Restaurants with maximum repeated customers
-- Insight: Measures brand loyalty and customer retention strength.
WITH repeat_customers AS (
    SELECT r_id, user_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY r_id, user_id
    HAVING COUNT(*) > 1
)
SELECT r.r_name, COUNT(rc.user_id) AS loyal_customers
FROM repeat_customers rc
JOIN restaurants r ON rc.r_id = r.r_id
GROUP BY r.r_name
ORDER BY loyal_customers DESC
LIMIT 1;


-- 🔹 7. Month-over-Month (MoM) Revenue Growth
-- Insight: Core business metric to track growth trajectory.
WITH monthly_revenue AS (
    SELECT 
        DATE_TRUNC('month', date) AS month,
        SUM(amount) AS revenue
    FROM orders
    GROUP BY month
)
SELECT 
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS prev_month,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month)) * 100.0 
        / NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 2
    ) AS growth_percent
FROM monthly_revenue;


-- 🔹 8. Customer favorite food (Ranked)
-- Insight: Foundation for a recommendation engine.
WITH food_count AS (
    SELECT o.user_id, od.f_id, COUNT(*) AS freq
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    GROUP BY o.user_id, od.f_id
),
ranked AS (
    SELECT *,
           RANK() OVER (PARTITION BY user_id ORDER BY freq DESC) AS rnk
    FROM food_count
)
SELECT u.name, f.f_name
FROM ranked r
JOIN users u ON r.user_id = u.user_id
JOIN food f ON r.f_id = f.f_id
WHERE r.rnk = 1;


-- 🔹 9. RFM Analysis (Recency, Frequency, Monetary)
-- Insight: Identifies high-value vs low-value customers.
SELECT 
    user_id,
    MAX(date) AS last_order_date,
    COUNT(order_id) AS frequency,
    SUM(amount) AS monetary
FROM orders
GROUP BY user_id;


-- 🔹 10. Most ordered dishes (corrected – replaces incorrect "top dishes by revenue")
-- Insight: Optimization of menu based on popularity.
SELECT f.f_name, COUNT(od.f_id) AS times_ordered
FROM order_details od
JOIN food f ON od.f_id = f.f_id
GROUP BY f.f_name
ORDER BY times_ordered DESC;


-- 🔹 11. Customer Segmentation (RFM Scoring)
-- Insight: Segmenting users into VIP, Medium, and Low Value for offers.
WITH rfm AS (
    SELECT 
        user_id,
        MAX(date) AS last_order,
        COUNT(order_id) AS frequency,
        SUM(amount) AS monetary
    FROM orders
    GROUP BY user_id
)
SELECT *,
    CASE 
        WHEN monetary > 1000 THEN 'High Value'
        WHEN monetary > 500 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS customer_segment
FROM rfm;


-- 🔹 12. Cohort Analysis (Retention)
-- Insight: Tracks how many users come back month after month.
WITH first_order AS (
    SELECT user_id, MIN(date) AS first_order_date
    FROM orders
    GROUP BY user_id
),
cohort AS (
    SELECT 
        o.user_id,
        DATE_TRUNC('month', f.first_order_date) AS cohort_month,
        DATE_TRUNC('month', o.date) AS order_month
    FROM orders o
    JOIN first_order f ON o.user_id = f.user_id
)
SELECT 
    cohort_month,
    order_month,
    COUNT(DISTINCT user_id) AS active_users
FROM cohort
GROUP BY cohort_month, order_month
ORDER BY cohort_month;


-- 🔹 13. Delivery Partner Performance
-- Insight: Operations improvement by analyzing delivery speed.
SELECT dp.partner_name,
       COUNT(o.order_id) AS total_orders,
       AVG(o.delivery_time) AS avg_delivery_time
FROM orders o
JOIN delivery_partner dp ON o.partner_id = dp.partner_id
GROUP BY dp.partner_name;


-- 🔹 14. Peak Order Time Analysis
-- NOTE: Removed because the `date` column is DATE (not TIMESTAMP). 
-- To analyze hourly trends, add a `order_time` TIME column to the schema.
-- Example (if a TIMESTAMP column existed):
-- SELECT EXTRACT(HOUR FROM order_datetime) AS order_hour, COUNT(*) 
-- FROM orders GROUP BY order_hour;