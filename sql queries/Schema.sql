-- Swiggy Data Analysis Schema

-- 1. Users Table
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- 2. Restaurants Table
CREATE TABLE restaurants (
    r_id INT PRIMARY KEY,
    r_name VARCHAR(255) NOT NULL,
    cuisine VARCHAR(100)
);

-- 3. Food Table
CREATE TABLE food (
    f_id INT PRIMARY KEY,
    f_name VARCHAR(255) NOT NULL,
    type VARCHAR(50) -- Veg or Non-veg
);

-- 4. Menu Table (Connects Restaurants and Food)
CREATE TABLE menu (
    menu_id INT PRIMARY KEY,
    r_id INT,
    f_id INT,
    price INT,
    FOREIGN KEY (r_id) REFERENCES restaurants(r_id),
    FOREIGN KEY (f_id) REFERENCES food(f_id)
);

-- 5. Delivery Partners Table
CREATE TABLE delivery_partner (
    partner_id INT PRIMARY KEY,
    partner_name VARCHAR(255) NOT NULL
);

-- 6. Orders Table
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT,
    r_id INT,
    amount INT,
    date DATE,
    partner_id INT,
    delivery_time INT,
    delivery_rating INT,
    restaurant_rating INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (r_id) REFERENCES restaurants(r_id),
    FOREIGN KEY (partner_id) REFERENCES delivery_partner(partner_id)
);

-- 7. Order Details Table (Mapping items to orders)
CREATE TABLE order_details (
    id INT PRIMARY KEY,
    order_id INT,
    f_id INT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (f_id) REFERENCES food(f_id)
);