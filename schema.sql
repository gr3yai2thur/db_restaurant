-- Active: 1790402056014@@127.0.0.1@3306@project69
-- ============================================================
--  schema.sql — ระบบร้านอาหาร (นิสิตออกแบบและเขียนเอง)
--  กติกา: 1 ออเดอร์มีหลายเมนู (M:N: order × menu_item ผ่าน order_item),
--         เมนูชุด combo = M:N (menu_item × menu_item)
--  ต้องมี: PK ทุกตาราง, FK ครบ, ชื่อตรงกับ db.py, sample data
-- ============================================================

-------- Drop Views --------
DROP VIEW IF EXISTS v_combo_detail;
DROP VIEW IF EXISTS v_order_total;
DROP VIEW IF EXISTS v_order_detail;

-------- Drop Tables --------
DROP TABLE IF EXISTS combo;
DROP TABLE IF EXISTS order_item;
DROP TABLE IF EXISTS food_order;
DROP TABLE IF EXISTS dining_table;
DROP TABLE IF EXISTS menu_item;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS customer;
-------- Show Tables --------
show tables;

-------- Tables --------
CREATE TABLE customer (
    -- TODO: name, phone, member_tier
    cust_id     INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    phone       VARCHAR(10) UNIQUE,
    member_tier ENUM('normal','silver','gold','vip') DEFAULT 'normal',
    points      INT NOT NULL DEFAULT 0
);

CREATE TABLE category (
    category_id   INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE menu_item (
    -- TODO: name, category, price, is_available
    item_id      INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    category_id  INT NOT NULL,
    price        INT NOT NULL CHECK (price >= 0),
    status       ENUM('available','sold_out','discontinued') NOT NULL DEFAULT 'available',
    CONSTRAINT fk_item_category FOREIGN KEY (category_id)
        REFERENCES category(category_id)
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
    cust_id      INT NOT NULL,
    table_id     INT NOT NULL,
    order_time   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status       ENUM('open','paid') NOT NULL DEFAULT 'open',
    payment_method ENUM('cash','card','qr') NULL,
CONSTRAINT fk_order_cust  FOREIGN KEY (cust_id)
        REFERENCES customer(cust_id),
CONSTRAINT fk_order_table FOREIGN KEY (table_id)
        REFERENCES dining_table(table_id)
);

CREATE TABLE order_item (       -- M:N: food_order × menu_item
    -- TODO: order_id (FK), item_id (FK), qty, note ; PRIMARY KEY (order_id, item_id)
    order_id    INT NOT NULL,
    item_id     INT NOT NULL,
    qty         INT NOT NULL CHECK (qty > 0),
    unit_price  INT NOT NULL CHECK (unit_price > 0),
    note        VARCHAR(100),
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

------- View --------

-------- รายละเอียด Order --------
CREATE VIEW v_order_total AS
SELECT
    o.order_id,
    o.cust_id,
    o.table_id,
    o.order_time,
    o.status,
    o.payment_method,
    SUM(oi.qty * oi.unit_price) AS total
FROM food_order o
JOIN order_item oi ON oi.order_id = o.order_id
GROUP BY o.order_id, o.cust_id, o.table_id,
         o.order_time, o.status, o.payment_method;

------- รายละเอียด Combo --------
CREATE VIEW v_combo_detail AS
SELECT
    cb.combo_id,
    main.name AS combo_name,
    main.price AS combo_price,
    added.name  AS includes_item,
    cb.amount
FROM combo cb
JOIN menu_item main ON main.item_id = cb.item_id
JOIN menu_item added  ON added.item_id  = cb.sub_item_id;

-------- รายละเอียด Order --------
CREATE VIEW v_order_detail AS
SELECT
    o.order_id,
    o.order_time,
    o.status,
    c.name AS customer_name,
    t.table_id,
    t.zone,
    m.name AS item_name,
    cat.name AS category,
    oi.qty,
    oi.unit_price,
    oi.qty * oi.unit_price AS total,
    oi.note
FROM food_order o
JOIN order_item oi   ON oi.order_id = o.order_id
JOIN menu_item m     ON m.item_id = oi.item_id
JOIN category cat    ON cat.category_id = m.category_id
JOIN dining_table t  ON t.table_id = o.table_id
JOIN customer c      ON c.cust_id = o.cust_id
ORDER BY o.order_id;

-------- Insert Data --------

-- TODO: INSERT ข้อมูลตัวอย่างทุกตาราง
INSERT INTO customer (name, phone, member_tier) VALUES
('Somchai Jaidee',   '0810000001', 'vip'),
('Suda Rakdee',      '0810000002', 'gold'),
('Mana Tangjai',     '0810000003', 'silver'),
('Piti Yindee',      '0810000004', 'normal'),
('Wichai Kengkaj',   '0810000005', 'normal');

INSERT INTO category (name) VALUES
('Pizza'),      -- 1
('Pasta'),      -- 2
('Burger'),     -- 3
('Salad'),      -- 4
('Steak'),      -- 5
('Japanese'),   -- 6
('Side'),       -- 7
('Beverage'),   -- 8
('Dessert'),    -- 9
('Combo');      -- 10

INSERT INTO menu_item (name, category_id, price, status) VALUES
('Margherita Pizza',           1, 259, 'available'),     -- 1
('Pepperoni Pizza',            1, 289, 'available'),     -- 2
('Spaghetti Carbonara',        2, 219, 'available'),     -- 3
('Spaghetti Bolognese',        2, 229, 'available'),     -- 4
('Classic Cheeseburger',       3, 189, 'available'),     -- 5
('BBQ Bacon Burger',           3, 229, 'available'),     -- 6
('Caesar Salad',               4, 159, 'available'),     -- 7
('Grilled Beef Steak',         5, 399, 'available'),     -- 8
('California Sushi Roll',      6, 199, 'available'),     -- 9
('Salmon Sashimi',             6, 249, 'sold_out'),      -- 10
('French Fries',               7,  79, 'available'),     -- 11
('Coca-Cola',                  8,  35, 'available'),     -- 12
('Iced Lemon Tea',             8,  45, 'available'),     -- 13
('Chocolate Lava Cake',        9, 129, 'available'),     -- 14
('Tiramisu',                   9, 139, 'available'),     -- 15
('Burger + Fries + Coke Set', 10, 249, 'available'),     -- 16
('Truffle Fries',              7,  99, 'discontinued');  -- 17

INSERT INTO dining_table (seats, zone) VALUES
(4, 'Indoor'),
(2, 'Indoor'),
(6, 'Outdoor'),
(4, 'VIP'),
(2, 'Outdoor');

INSERT INTO food_order (cust_id, table_id, order_time, status, payment_method) VALUES
(1, 2, '2026-09-24 12:15:00', 'paid', 'card'),
(2, 1, '2026-09-24 13:00:00', 'paid', 'cash'),
(3, 4, '2026-09-25 18:30:00', 'paid', 'qr'),
(5, 3, '2026-09-25 19:10:00', 'paid', 'cash'),
(1, 2, '2026-09-25 20:00:00', 'paid', 'qr'),
(4, 5, '2026-09-26 11:45:00', 'open', NULL);

INSERT INTO order_item (order_id, item_id, qty, unit_price, note) VALUES
-- order 1: Margherita Pizza x1, Coke x2
(1, 1,  1, 259, NULL),
(1, 12, 2,  35, NULL),
-- order 2: Carbonara x1, Caesar Salad x1, Lemon Tea x1
(2, 3,  1, 219, 'Extra cheese'),
(2, 7,  1, 159, NULL),
(2, 13, 1,  45, NULL),
-- order 3: Beef Steak x1, Fries x2, Bolognese x1 (รวม 786 เกิน 500)
(3, 8,  1, 399, 'Medium rare'),
(3, 11, 2,  79, NULL),
(3, 4,  1, 229, NULL),
-- order 4: Cheeseburger x4, Coke x4
(4, 5,  4, 189, NULL),
(4, 12, 4,  35, NULL),
-- order 5: BBQ Bacon Burger x2, Carbonara x1, Lemon Tea x2
(5, 6,  2, 229, NULL),
(5, 3,  1, 219, NULL),
(5, 13, 2,  45, NULL),
-- order 6: Combo Set x1 (ยัง open อยู่)
(6, 16, 1, 249, NULL);

INSERT INTO combo (item_id, sub_item_id, amount) VALUES
(16, 5, 1),   -- Classic Cheeseburger
(16, 11, 1),  -- French Fries
(16, 12, 1);  -- Coca-Cola
--   ★ ควรมีออเดอร์ status 'open' อย่างน้อย 1 โต๊ะ ไว้ทดสอบ "เปิดออเดอร์ซ้ำโต๊ะเดิมไม่ได้"



SELECT * FROM combo;
select * from v_combo_detail;

SELECT * 
FROM v_order_total;