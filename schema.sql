-- Active: 1790402056014@@127.0.0.1@3306@project69
-- ============================================================
--  schema.sql — ระบบร้านอาหาร (นิสิตออกแบบและเขียนเอง)
--  กติกา: 1 ออเดอร์มีหลายเมนู (M:N: order × menu_item ผ่าน order_item),
--         เมนูชุด combo = M:N (menu_item × menu_item)
--  ต้องมี: PK ทุกตาราง, FK ครบ, ชื่อตรงกับ db.py, sample data
-- ============================================================
DROP Table if EXISTS customer

DROP Table if EXISTS menu_item

DROP Table if EXISTS dining_table

DROP Table if EXISTS food_order

DROP Table if EXISTS order_item

DROP Table if EXISTS combo

show tables



CREATE TABLE customer (
    cust_id INT AUTO_INCREMENT PRIMARY KEY
    -- TODO: name, phone, member_tier
    
);
CREATE TABLE menu_item (
    item_id INT AUTO_INCREMENT PRIMARY KEY
    -- TODO: name, category, price, is_available
);
CREATE TABLE dining_table (
    table_id INT AUTO_INCREMENT PRIMARY KEY
    -- TODO: seats, zone
);
CREATE TABLE food_order (
    order_id INT AUTO_INCREMENT PRIMARY KEY
    -- TODO: cust_id (FK), table_id (FK), order_time (DATETIME), status ENUM('open','paid')
    -- ★ ไม่ต้องมีคอลัมน์ยอดรวม — คำนวณจาก order_item × menu_item (ดู search_orders ใน db.py)
);
CREATE TABLE order_item (         -- M:N: food_order × menu_item
    -- TODO: order_id (FK), item_id (FK), qty, note ; PRIMARY KEY (order_id, item_id)
    order_id INT, item_id INT
);
CREATE TABLE combo (              -- M:N: menu_item × menu_item
    combo_id INT AUTO_INCREMENT PRIMARY KEY
    -- TODO: item_id (FK -> menu_item), sub_item_id (FK -> menu_item), amount
);


-- TODO: INSERT ข้อมูลตัวอย่างทุกตาราง
--   ★ ควรมีออเดอร์ status 'open' อย่างน้อย 1 โต๊ะ ไว้ทดสอบ "เปิดออเดอร์ซ้ำโต๊ะเดิมไม่ได้"
