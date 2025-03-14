import sqlite3

conn = sqlite3.connect("bot_database.db", check_same_thread=False)
cur = conn.cursor()

# إنشاء جدول الخدمات
cur.execute("""
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    price INTEGER,
    request_info TEXT
)
""")

# إضافة خدمة جديدة
def add_service(name, price, request_info):
    cur.execute("INSERT INTO services (name, price, request_info) VALUES (?, ?, ?)", (name, price, request_info))
    conn.commit()

# تحديث سعر خدمة
def update_service_price(name, new_price):
    cur.execute("UPDATE services SET price = ? WHERE name = ?", (new_price, name))
    conn.commit()

# جلب الإحصائيات
def get_stats():
    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'completed'")
    completed_orders = cur.fetchone()[0]

    cur.execute("SELECT SUM(price) FROM orders WHERE status = 'completed'")
    total_points = cur.fetchone()[0] or 0

    return {"users": users, "completed_orders": completed_orders, "total_points": total_points}

# سجل العمليات
def get_logs():
    cur.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 10")
    return cur.fetchall()

# تسجيل عملية
def log_operation(user_id, action, details):
    cur.execute("INSERT INTO logs (user_id, action, details) VALUES (?, ?, ?)", (user_id, action, details))
    conn.commit()