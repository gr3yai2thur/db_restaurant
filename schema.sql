-- Active: 1790402056014@@127.0.0.1@3306@project69
-- ============================================================
--  schema.sql — ระบบร้านอาหาร (นิสิตออกแบบและเขียนเอง)
--  กติกา: 1 ออเดอร์มีหลายเมนู (M:N: order × menu_item ผ่าน order_item),
--         เมนูชุด combo = M:N (menu_item × menu_item)
--  ต้องมี: PK ทุกตาราง, FK ครบ, ชื่อตรงกับ db.py, sample data
-- ============================================================
DROP TABLE IF EXISTS combo;
DROP TABLE IF EXISTS order_item;
DROP TABLE IF EXISTS food_order;
DROP TABLE IF EXISTS dining_table;
DROP TABLE IF EXISTS menu_item;
DROP TABLE IF EXISTS customer;

show tables

CREATE TABLE customer (
    -- TODO: name, phone, member_tier
    cust_id     INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    phone       VARCHAR(10) UNIQUE,
    member_tier VARCHAR(50) DEFAULT 'normal'
    
);
CREATE TABLE menu_item (
    -- TODO: name, category, price, is_available
    item_id     INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR (100) NOT NULL,
    category    VARCHAR (100) NOT NULL,
    price       INT NOT NULL,
    is_available VARCHAR(50) DEFAULT 'available'
);
CREATE TABLE dining_table (
    -- TODO: seats, zone
    table_id    INT AUTO_INCREMENT PRIMARY KEY,
    seats       INT NOT NULL,
    zone        VARCHAR (50)
);
CREATE TABLE food_order (
    -- TODO: cust_id (FK), table_id (FK), order_time (DATETIME), status ENUM('open','paid')
    -- ★ ไม่ต้องมีคอลัมน์ยอดรวม — คำนวณจาก order_item × menu_item (ดู search_orders ใน db.py)
    order_id     INT AUTO_INCREMENT PRIMARY KEY,
    cust_id      INT NULL,
    table_id     INT NOT NULL,
    order_time   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status       ENUM('open','paid') NOT NULL DEFAULT 'open',
CONSTRAINT fk_order_cust  FOREIGN KEY (cust_id)
        REFERENCES customer(cust_id),
CONSTRAINT fk_order_table FOREIGN KEY (table_id)
        REFERENCES dining_table(table_id)
);
CREATE TABLE order_item (         -- M:N: food_order × menu_item
    -- TODO: order_id (FK), item_id (FK), qty, note ; PRIMARY KEY (order_id, item_id)
    order_id    INT NOT NULL, 
    item_id     INT NOT NULL, 
    qty         INT NOT NULL,
    note        VARCHAR (100),
CONSTRAINT pk_order_item    PRIMARY KEY (order_id, item_id),
CONSTRAINT fk_orderitem_order  FOREIGN KEY (order_id)  
    REFERENCES food_order(order_id),
CONSTRAINT fk_orderitem_item  FOREIGN KEY (item_id)  
    REFERENCES menu_item(item_id) 
);
CREATE TABLE combo (              -- M:N: menu_item × menu_item
    combo_id    INT AUTO_INCREMENT PRIMARY KEY,
    item_id     INT NOT NULL,
    sub_item_id INT NOT NULL,
    amount      INT NOT NULL,
CONSTRAINT  fk_combo_itemid FOREIGN KEY (item_id)  
    REFERENCES menu_item(item_id),
CONSTRAINT  fk_combo_subitem FOREIGN KEY (sub_item_id)  
    REFERENCES menu_item(item_id),
CONSTRAINT uq_combo_pair UNIQUE (item_id, sub_item_id),
CONSTRAINT chk_combo_not_self CHECK (item_id <> sub_item_id)    
    -- TODO: item_id (FK -> menu_item), sub_item_id (FK -> menu_item), amount
);


-- TODO: INSERT ข้อมูลตัวอย่างทุกตาราง
INSERT INTO customer (name, phone, member_tier) VALUES
('Somchai Jaidee',   '0810000001', 'vip'),
('Suda Rakdee',      '0810000002', 'gold'),
('Mana Tangjai',     '0810000003', 'silver'),
('Piti Yindee',      '0810000004', 'normal'),
('Wichai Kengkaj',   '0810000005', 'normal');

INSERT INTO menu_item (name, category, price, is_available) VALUES
('Margherita Pizza',      'Pizza',      259, 'available'),
('Pepperoni Pizza',       'Pizza',      289, 'available'),
('Spaghetti Carbonara',   'Pasta',      219, 'available'),
('Spaghetti Bolognese',   'Pasta',      229, 'available'),
('Classic Cheeseburger',  'Burger',     189, 'available'),
('BBQ Bacon Burger',      'Burger',     229, 'available'),
('Caesar Salad',          'Salad',      159, 'available'),
('Grilled Beef Steak',    'Steak',      399, 'available'),
('California Sushi Roll', 'Japanese',   199, 'available'),
('Salmon Sashimi',        'Japanese',   249, 'sold_out'),
('French Fries',          'Side',        79, 'available'),
('Coca-Cola',             'Beverage',    35, 'available'),
('Iced Lemon Tea',        'Beverage',    45, 'available'),
('Chocolate Lava Cake',   'Dessert',    129, 'available'),
('Tiramisu',              'Dessert',    139, 'available'),
('Burger + Fries + Coke Set', 'Combo',  249, 'available');

INSERT INTO dining_table (seats, zone) VALUES
(4, 'Indoor'),
(2, 'Indoor'),
(6, 'Outdoor'),
(4, 'VIP'),
(2, 'Outdoor');

INSERT INTO food_order (cust_id, table_id, order_time, status) VALUES
(1, 2, '2026-09-24 12:15:00', 'paid'),
(2, 1, '2026-09-24 13:00:00', 'paid'),
(3, 4, '2026-09-25 18:30:00', 'paid'),
(NULL, 3, '2026-09-25 19:10:00', 'paid'),
(1, 2, '2026-09-25 20:00:00', 'paid'),
(4, 5, '2026-09-26 11:45:00', 'open');

INSERT INTO order_item (order_id, item_id, qty, note) VALUES
-- order 1: Margherita Pizza x1, Coke x2
(1, 1, 1, NULL),
(1, 12, 2, NULL),
-- order 2: Carbonara x1, Caesar Salad x1, Lemon Tea x1
(2, 3, 1, 'Extra cheese'),
(2, 7, 1, NULL),
(2, 13, 1, NULL),
-- order 3: Beef Steak x1, Fries x2, Bolognese x1  (รวมเกิน 500)
(3, 8, 1, 'Medium rare'),
(3, 11, 2, NULL),
(3, 4, 1, NULL),
-- order 4: Cheeseburger x4, Coke x4
(4, 5, 4, NULL),
(4, 12, 4, NULL),
-- order 5: BBQ Bacon Burger x2, Carbonara x1, Lemon Tea x2
(5, 6, 2, NULL),
(5, 3, 1, NULL),
(5, 13, 2, NULL),
-- order 6: Combo Set x1 (ยัง open อยู่)
(6, 16, 1, NULL);

INSERT INTO combo (item_id, sub_item_id, amount) VALUES
(16, 5, 1),   -- Classic Cheeseburger
(16, 11, 1),  -- French Fries
(16, 12, 1);  -- Coca-Cola
--   ★ ควรมีออเดอร์ status 'open' อย่างน้อย 1 โต๊ะ ไว้ทดสอบ "เปิดออเดอร์ซ้ำโต๊ะเดิมไม่ได้"
