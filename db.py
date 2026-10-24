# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล  ★★★ นิสิตเขียน SQL ในไฟล์นี้ ★★★
#  มองหาคำว่า  # TODO  ทุกฟังก์ชัน — ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
# ============================================================
import mysql.connector
import config


def get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD,
        database=config.DB_NAME, port=config.DB_PORT)


def run_query(sql, params=None):
    """รัน SELECT คืนผลเป็น list ของ dict"""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute(sql, params or ()); rows = cur.fetchall()
    cur.close(); conn.close(); return rows


def run_command(sql, params=None):
    """รัน INSERT / UPDATE / DELETE แล้ว commit"""
    conn = get_connection(); cur = conn.cursor()
    cur.execute(sql, params or ()); conn.commit()
    out = {"new_id": cur.lastrowid, "affected": cur.rowcount}
    cur.close(); conn.close(); return out


def blank_to_none(value):
    """ช่องที่ไม่ได้กรอกในฟอร์มจะส่งมาเป็น "" — แปลงเป็น None (= NULL ใน SQL)
    ใช้กับคอลัมน์ที่ว่างได้ เช่น return_date, paid_date  เพราะ MySQL ไม่รับ '' เป็น DATE"""
    return None if value in ("", None) else value


def _todo(name):
    raise NotImplementedError(f"TODO: ยังไม่ได้เขียนฟังก์ชัน {name} ใน db.py")


# ---------- ลูกค้า (customer) ----------
def search_customers(filters):
    """ค้นหา ลูกค้า ตามเงื่อนไข (name, phone, member_tier)"""
    sql = "SELECT * FROM customer WHERE 1=1"
    params = []

    name = filters.get("name")
    if name:
        sql += " AND name LIKE %s"
        params.append(f"%{name}%")

    phone = filters.get("phone")
    if phone:
        sql += " AND phone LIKE %s"
        params.append(f"%{phone}%")

    member_tier = filters.get("member_tier")
    if member_tier:
        sql += " AND member_tier = %s"
        params.append(member_tier)

    sql += " ORDER BY cust_id"

    return run_query(sql, params)


def get_customer(cust_id):
    """ดึง ลูกค้า 1 รายการตาม cust_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    rows = run_query("SELECT * FROM customer WHERE cust_id = %s", (cust_id,))
    return rows[0] if rows else None


def create_customer(data):
    """เพิ่ม ลูกค้า ใหม่ — data มีคีย์: name, phone, member_tier"""
    if (len(data["phone"]) != 10):
        raise ValueError("กรุณากรอกเบอร์ให้ถูกต้อง")
    return run_command(
        "INSERT INTO customer (name, gender, phone, member_tier, points) "
        "VALUES (%s, %s, %s, %s, %s)",
        (data["name"], data["gender"], blank_to_none(data["phone"]), data["member_tier"], data["points"])
    )


def update_customer(cust_id, data):
    """แก้ไข ลูกค้า ตาม cust_id"""
    if (len(data["phone"]) != 10):
        raise ValueError("กรุณากรอกเบอร์ให้ถูกต้อง")
    return run_command(
        "UPDATE customer SET name = %s, gender = %s, phone = %s, "
        "member_tier = %s, points = %s WHERE cust_id = %s",
        (data["name"], data["gender"], blank_to_none(data["phone"]),
         data["member_tier"], data["points"], cust_id,)
    )


def delete_customer(cust_id):
    """ลบ ลูกค้า ตาม cust_id"""
    return run_command(
        "DELETE FROM customer WHERE cust_id = %s",
        (cust_id,)
    )

# ---------- เมนูอาหาร (menu_item) ----------
def search_items(filters):
    """ค้นหา เมนูอาหาร ตามเงื่อนไข (name, category)"""
    sql = (
        "SELECT m.item_id, m.name, c.name AS category, m.price, m.status "
        "FROM menu_item m "
        "JOIN category c ON c.category_id = m.category_id "
        "WHERE 1=1"
    )
    params = []

    name = filters.get("name")
    if name:
        sql += " AND m.name LIKE %s"
        params.append(f"%{name}%")

    category = filters.get("category")
    if category:
        sql += " AND c.name LIKE %s"
        params.append(f"%{category}%")

    category_id = filters.get("category_id")
    if category_id:
        sql += " AND m.category_id = %s"
        params.append(category_id)

    status = filters.get("status")
    if status:
        sql += " AND m.status = %s"
        params.append(status)

    sql += " ORDER BY m.item_id"

    return run_query(sql, params)


def get_item(item_id):
    """ดึง เมนูอาหาร 1 รายการตาม item_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    rows = run_query(
        "SELECT * FROM menu_item WHERE item_id = %s",
        (item_id,)
    )
    return rows[0] if rows else None


def create_item(data):
    """เพิ่ม เมนูอาหาร ใหม่ — data มีคีย์: name, category_id, price, status"""
    return run_command(
        "INSERT INTO menu_item (name, category_id, price, status) "
        "VALUES (%s, %s, %s, %s)",
        (data["name"], data["category_id"], data["price"], data["status"])
    )


def update_item(item_id, data):
    """แก้ไข เมนูอาหาร ตาม item_id"""
    return run_command(
        "UPDATE menu_item SET name = %s, category_id = %s, price = %s, "
        "status = %s WHERE item_id = %s",
        (data["name"], data["category_id"], data["price"],
         data["status"], item_id,)
    )


def delete_item(item_id):
    """ลบ เมนูอาหาร ตาม item_id"""
    return run_command(
        "DELETE FROM menu_item WHERE item_id = %s",
        (item_id,)
    )

# ---------- ออเดอร์ (food_order) ----------
def search_orders(filters):
    """ค้นหา ออเดอร์ ตามเงื่อนไข (cust_id, table_id, status)"""
    sql = (
        "SELECT o.order_id, o.cust_id, c.name AS customer_name, "
        "       o.table_id, o.order_time, o.status, "
        "       IFNULL(t.total, 0) AS total, "
        "       o.discount, "
        "       IFNULL(t.total, 0) - o.discount AS balance "
        "FROM food_order o "
        "JOIN customer c ON c.cust_id = o.cust_id "
        "LEFT JOIN ("
        "    SELECT order_id, SUM(qty * unit_price) AS total "
        "    FROM order_item "
        "    GROUP BY order_id"
        ") t ON t.order_id = o.order_id "
        "WHERE 1=1"
    )
    params = []

    cust_id = filters.get("cust_id")
    if cust_id:
        sql += " AND o.cust_id = %s"
        params.append(cust_id)

    table_id = filters.get("table_id")
    if table_id:
        sql += " AND o.table_id = %s"
        params.append(table_id)

    status = filters.get("status")
    if status:
        sql += " AND o.status = %s"
        params.append(status)

    sql += " ORDER BY o.order_id"

    return run_query(sql, params)


def get_order(order_id):
    """ดึง ออเดอร์ 1 รายการตาม order_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    rows = run_query(
        "SELECT * FROM food_order WHERE order_id = %s",
        (order_id,)
    )
    return rows[0] if rows else None


def check_table_free(table_id, order_id=None):
    """ตรวจก่อนเปิดออเดอร์ (status = 'open') — ถ้าไม่ผ่านให้ raise ValueError("ข้อความ")"""
    # 1) โต๊ะต้องมีอยู่จริง
    rows = run_query(
        "SELECT table_id FROM dining_table WHERE table_id = %s",
        (table_id,)
    )
    if not rows:
        raise ValueError(f"ไม่พบโต๊ะ {table_id}")

    # 2) โต๊ะต้องว่าง = ไม่มีออเดอร์อื่นที่ยัง 'open'
    n = run_query(
        "SELECT COUNT(*) AS n FROM food_order "
        "WHERE table_id = %s AND status = 'open' AND order_id <> %s",
        (table_id, order_id or 0,)
    )[0]["n"]
    if n > 0:
        raise ValueError(f"โต๊ะ {table_id} ยังมีออเดอร์ที่ยังไม่ชำระเงิน")


def calculate_order_discount(order_id):
    """คำนวณและอัปเดตส่วนลดของออเดอร์ตาม member_tier และยอดรวม
    คืนค่า: (subtotal, discount_amount, final_total)"""
    # ดึงข้อมูลออเดอร์และลูกค้า
    order_info = run_query(
        "SELECT o.order_id, c.member_tier "
        "FROM food_order o "
        "JOIN customer c ON c.cust_id = o.cust_id "
        "WHERE o.order_id = %s",
        (order_id,)
    )
    if not order_info:
        return (0, 0, 0)
    
    tier = order_info[0]['member_tier']
    
    # คำนวณยอดรวมจาก order_item
    total_row = run_query(
        "SELECT IFNULL(SUM(qty * unit_price), 0) AS total "
        "FROM order_item WHERE order_id = %s",
        (order_id,)
    )
    subtotal = int(total_row[0]['total']) if total_row else 0
    
    # คำนวณเปอร์เซ็นต์ส่วนลดตาม tier
    discount_percent = {
        'normal': 0,
        'silver': 5,
        'gold': 10,
        'vip': 15
    }.get(tier, 0)
    
    # คำนวณจำนวนเงินส่วนลด
    discount_amount = int(subtotal * discount_percent / 100)
    final_total = subtotal - discount_amount
    
    # อัปเดตส่วนลดในฐานข้อมูล
    run_command(
        "UPDATE food_order SET discount = %s WHERE order_id = %s",
        (discount_amount, order_id)
    )
    
    return (subtotal, discount_amount, final_total)


def create_order(data):
    """เพิ่ม ออเดอร์ ใหม่ — data มีคีย์: cust_id, table_id, order_time, status"""
    if data["status"] == "open":
        check_table_free(data["table_id"])
    
    # สร้างออเดอร์ (discount = 0 เพราะยังไม่มี order_item)
    result = run_command(
        "INSERT INTO food_order (cust_id, table_id, order_time, status, payment_method, discount) "
        "VALUES (%s, %s, IFNULL(%s, NOW()), %s, %s, 0)",
        (data["cust_id"], data["table_id"],
         blank_to_none(data["order_time"]), data["status"],
         blank_to_none(data.get("payment_method", "")))
    )
    
    return result


def update_order(order_id, data):
    """แก้ไข ออเดอร์ ตาม order_id"""
    if data["status"] == "open":
        check_table_free(data["table_id"], order_id)

    # ดึง status และ cust_id ปัจจุบันของออเดอร์ก่อนเปลี่ยนแปลง
    current = run_query(
        "SELECT status, cust_id FROM food_order WHERE order_id = %s",
        (order_id,)
    )

    # ห้ามแก้กลับจาก paid → open
    if current and current[0]["status"] == "paid" and data["status"] == "open":
        raise ValueError("ออเดอร์ที่ชำระเงินแล้วไม่สามารถเปลี่ยนสถานะกลับได้")

    # ถ้าเปลี่ยน status เป็น 'paid' → บวก points ให้ลูกค้าอัตโนมัติ
    if data["status"] == "paid":
        # ตรวจว่า status เดิมยังเป็น 'open' อยู่ (กัน double points)
        if current and current[0]["status"] == "open":
            cust_id = current[0]["cust_id"]
            # คำนวณยอดรวมออเดอร์จาก order_item (ยอดก่อนลด)
            total_row = run_query(
                "SELECT IFNULL(SUM(qty * unit_price), 0) AS total "
                "FROM order_item WHERE order_id = %s",
                (order_id,)
            )
            total = int(total_row[0]["total"]) if total_row else 0
            # 1 point ต่อทุก 10 บาท (คิดจากยอดก่อนลด)
            earned = total // 10
            if earned > 0:
                run_command(
                    "UPDATE customer SET points = points + %s WHERE cust_id = %s",
                    (earned, cust_id)
                )
            # อัปเกรด member_tier อัตโนมัติตาม points สะสม
            pts_row = run_query(
                "SELECT points FROM customer WHERE cust_id = %s", (cust_id,)
            )
            if pts_row:
                total_pts = pts_row[0]["points"]
                new_tier = (
                    "vip"    if total_pts >= 2000 else
                    "gold"   if total_pts >= 1000 else
                    "silver" if total_pts >= 500  else
                    "normal"
                )
                run_command(
                    "UPDATE customer SET member_tier = %s WHERE cust_id = %s",
                    (new_tier, cust_id)
                )

    # อัปเดตออเดอร์
    result = run_command(
        "UPDATE food_order SET cust_id = %s, table_id = %s, "
        "order_time = IFNULL(%s, order_time), status = %s, payment_method = %s "
        "WHERE order_id = %s",
        (data["cust_id"], data["table_id"],
         blank_to_none(data["order_time"]), data["status"],
         blank_to_none(data.get("payment_method", "")), order_id,)
    )
    
    # ถ้ามีการเปลี่ยนลูกค้า → คำนวณส่วนลดใหม่
    if current and current[0]["cust_id"] != data["cust_id"]:
        calculate_order_discount(order_id)
    
    return result


def delete_order(order_id):
    """ลบ ออเดอร์ ตาม order_id"""
    return run_command(
        "DELETE FROM food_order WHERE order_id = %s",
        (order_id,)
    )


# ---------- รายการอาหารในออเดอร์ (order_item) ----------
def search_order_items(filters):
    """ค้นหา รายการอาหาร ตามเงื่อนไข (order_id, table_id, item_name, status)"""
    sql = (
        "SELECT oi.order_id, o.table_id, m.name AS item_name, "
        "       oi.qty, oi.unit_price, (oi.qty * oi.unit_price) AS subtotal, "
        "       oi.note, m.status "
        "FROM order_item oi "
        "JOIN food_order o ON o.order_id = oi.order_id "
        "JOIN menu_item m  ON m.item_id  = oi.item_id "
        "WHERE 1=1"
    )
    params = []

    order_id = filters.get("order_id")
    if order_id:
        sql += " AND oi.order_id = %s"
        params.append(order_id)

    table_id = filters.get("table_id")
    if table_id:
        sql += " AND o.table_id = %s"
        params.append(table_id)

    name = filters.get("name")
    if name:
        sql += " AND m.name LIKE %s"
        params.append(f"%{name}%")

    status = filters.get("status")
    if status:
        sql += " AND m.status = %s"
        params.append(status)

    sql += " ORDER BY oi.order_id, m.name"
    return run_query(sql, params)


def get_order_item(order_id, item_id):
    """ดึง รายการอาหาร 1 แถว ตาม (order_id, item_id)"""
    rows = run_query(
        "SELECT oi.order_id, oi.item_id, m.name AS item_name, "
        "       oi.qty, oi.unit_price, oi.note "
        "FROM order_item oi "
        "JOIN menu_item m ON m.item_id = oi.item_id "
        "WHERE oi.order_id = %s AND oi.item_id = %s",
        (order_id, item_id)
    )
    return rows[0] if rows else None


def create_order_item(data):
    """เพิ่มเมนูเข้าออเดอร์ — data มีคีย์: order_id, item_id, qty, note
    unit_price คัดลอกจากราคาปัจจุบันของเมนู อัตโนมัติ"""
    # ตรวจว่าออเดอร์มีอยู่จริงและยังเป็น open
    order_check = run_query(
        "SELECT status FROM food_order WHERE order_id = %s",
        (data["order_id"],)
    )
    if not order_check:
        raise ValueError(f"ไม่พบออเดอร์ order_id={data['order_id']}")
    if order_check[0]["status"] == "paid":
        raise ValueError("ไม่สามารถสั่งอาหารเพิ่มในออเดอร์ที่ชำระเงินแล้ว")
    
    rows = run_query(
        "SELECT price, status FROM menu_item WHERE item_id = %s",
        (data["item_id"],)
    )
    if not rows:
        raise ValueError(f"ไม่พบเมนู item_id={data['item_id']}")
    if rows[0]["status"] != "available":
        raise ValueError("เมนูนี้ไม่พร้อมขาย!")
    unit_price = rows[0]["price"]

    # เมนูเดิมในออเดอร์เดียวกันมีได้เพียงหนึ่งแถว
    # ถ้ามีอยู่แล้วให้เพิ่มจำนวน; ถ้ายังไม่มีจึงเพิ่มแถวใหม่
    existing = run_query(
        "SELECT qty FROM order_item WHERE order_id = %s AND item_id = %s",
        (data["order_id"], data["item_id"])
    )
    if existing:
        result = run_command(
            "UPDATE order_item SET qty = qty + %s, note = %s "
            "WHERE order_id = %s AND item_id = %s",
            (data.get("qty", 1), blank_to_none(data.get("note", "")),
             data["order_id"], data["item_id"])
        )
    else:
        result = run_command(
            "INSERT INTO order_item (order_id, item_id, qty, unit_price, note) "
            "VALUES (%s, %s, %s, %s, %s)",
            (data["order_id"], data["item_id"], data.get("qty", 1),
             unit_price, blank_to_none(data.get("note", "")))
        )
    
    # คำนวณส่วนลดใหม่ (เพราะยอดรวมเปลี่ยน)
    calculate_order_discount(data["order_id"])
    
    return result


def update_order_item(order_id, item_id, data):
    """แก้ไข qty / note ของ order_item"""
    result = run_command(
        "UPDATE order_item SET qty = %s, note = %s "
        "WHERE order_id = %s AND item_id = %s",
        (data["qty"], blank_to_none(data.get("note", "")), order_id, item_id)
    )
    
    # คำนวณส่วนลดใหม่ (เพราะยอดรวมเปลี่ยน)
    calculate_order_discount(order_id)
    
    return result


def delete_order_item(order_id, item_id):
    """ลบ รายการอาหาร ออกจากออเดอร์"""
    result = run_command(
        "DELETE FROM order_item WHERE order_id = %s AND item_id = %s",
        (order_id, item_id)
    )
    
    # คำนวณส่วนลดใหม่ (เพราะยอดรวมเปลี่ยน)
    calculate_order_discount(order_id)
    
    return result


# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
#  ★ ชื่อคอลัมน์ใน SELECT จะกลายเป็นหัวตารางบนเว็บ — ใช้ AS 'ชื่อภาษาไทย' ได้
# ============================================================
def report_summary():
    """ตัวเลขสรุปบนการ์ด dashboard — คืน dict {ชื่อการ์ด: ตัวเลข}"""
    sql = """SELECT
               (SELECT COUNT(*) FROM customer)   AS 'ลูกค้า',
               (SELECT COUNT(*) FROM menu_item)  AS 'เมนู',
               (SELECT COUNT(*) FROM food_order) AS 'ออเดอร์',
               (SELECT IFNULL(SUM(qty * unit_price), 0)
                  FROM order_item)               AS 'ยอดขายรวม',
               (SELECT COUNT(*) FROM food_order
                 WHERE status = 'open')          AS 'ออเดอร์ที่ยังไม่จ่าย',
               (SELECT IFNULL(ROUND(SUM(oi.qty * oi.unit_price)
                                    / COUNT(DISTINCT oi.order_id)), 0)
                  FROM order_item oi
                 INNER JOIN food_order o ON o.order_id = oi.order_id
                 WHERE o.status = 'paid')        AS 'ยอดเฉลี่ยต่อบิล'
          """
    return run_query(sql)[0]

    # TODO: ระหว่างที่ยังไม่ได้เขียน SQL คืนค่า None ให้การ์ดแสดง "—" รอไว้
    return {
        "ลูกค้า":         None,   # (SELECT COUNT(*) FROM customer)
        "เมนู":           None,   # นับเมนูทั้งหมด
        "ออเดอร์":        None,   # นับออเดอร์ทั้งหมด
        "ยอดขายรวม":      None,   # IFNULL(SUM(qty × price), 0) จาก order_item JOIN menu_item
        "คิดเพิ่มเอง 1":  None,   # ตั้งชื่อการ์ดใหม่ + เขียน SQL เอง
        "คิดเพิ่มเอง 2":  None,   # ตั้งชื่อการ์ดใหม่ + เขียน SQL เอง
    }

def report_popular_items():
    """📈 เมนูขายดี (Best Sellers)"""
    return run_query(
        "SELECT m.item_id, m.name, SUM(oi.qty) AS total_qty "
        "FROM order_item oi "
        "JOIN menu_item m ON m.item_id = oi.item_id "
        "GROUP BY m.item_id, m.name "
        "ORDER BY total_qty DESC, m.item_id "
        "LIMIT 5"
    )

def report_daily_sales():
    """💰 ยอดขายรวมต่อวัน (Daily Sales)"""
    return run_query(
        "SELECT DATE(o.order_time) AS day, "
        "SUM(oi.qty * oi.unit_price) AS total_sales "
        "FROM food_order o "
        "JOIN order_item oi ON oi.order_id = o.order_id "
        "GROUP BY DATE(o.order_time) "
        "ORDER BY day"
    )

def report_big_orders():
    """🧾 ออเดอร์ยอดเกิน 500 บาท (HAVING)"""
    return run_query(
        "SELECT o.order_id, o.table_id, o.order_time, "
        "SUM(oi.qty * oi.unit_price) AS total "
        "FROM food_order o "
        "JOIN order_item oi ON oi.order_id = o.order_id "
        "GROUP BY o.order_id, o.table_id, o.order_time "
        "HAVING SUM(oi.qty * oi.unit_price) > 500 "
        "ORDER BY total DESC"
    )


def report_payment_method_sales():
    """💳 ยอดขายแยกตามวิธีชำระเงิน (เฉพาะออเดอร์ที่ชำระแล้ว)"""
    return run_query(
        "SELECT IFNULL(o.payment_method, 'unspecified') AS payment_method, "
        "COUNT(DISTINCT o.order_id) AS order_count, "
        "SUM(t.subtotal - o.discount) AS totals "
        "FROM food_order o "
        "JOIN ("
        "    SELECT order_id, SUM(qty * unit_price) AS subtotal "
        "    FROM order_item "
        "    GROUP BY order_id"
        ") t ON t.order_id = o.order_id "
        "WHERE o.status = 'paid' "
        "GROUP BY o.payment_method "
        "ORDER BY totals DESC"
    )

# ============================================================
#  รายการรายงานที่แสดงบนหน้า /report  (เรียงตามลำดับที่แสดง)
#  ★ วิธีเพิ่มรายงานใหม่ (ไม่ต้องแก้ไฟล์อื่น):
#    1) เขียนฟังก์ชัน report_xxx() ด้านบน ให้ return run_query(sql)
#    2) เพิ่ม 1 บรรทัดในรายการนี้:  ("ชื่อใน-url", "หัวข้อที่แสดง", ชื่อฟังก์ชัน)
#  ★ รายการนี้ต้องอยู่ท้ายไฟล์ (หลังฟังก์ชันทั้งหมด) ไม่งั้น Python หาชื่อฟังก์ชันไม่เจอ
#  ★ ห้ามตั้งชื่อ url ว่า "summary" (ใช้แล้วสำหรับการ์ดสรุป)
# ============================================================
REPORTS = [
    ("popular-items", "📈 เมนูขายดี (Best Sellers)",        report_popular_items),
    ("daily-sales",   "💰 ยอดขายรวมต่อวัน (Daily Sales)",   report_daily_sales),
    ("big-orders",    "🧾 ออเดอร์ยอดเกิน 500 บาท (HAVING)", report_big_orders),
    ("payment-method-sales", "💳 ยอดขายแยกตามวิธีชำระเงิน", report_payment_method_sales),
    # ("my-report", "📋 รายงานของฉัน", report_my_report),   ← ตัวอย่างการเพิ่มรายงานที่ 4
]
