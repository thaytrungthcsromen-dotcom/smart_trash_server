import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

STUDENTS_DATA = [
    ("101", "Cil Múp Akian"),
    ("102", "Khuất Ngọc Anh"),
    ("103", "Dơng Gur Lý Châu"),
    ("104", "Nguyễn Thành Danh"),
    ("105", "Kiều Minh Đức"),
    ("106", "Nguyễn Hương Giang"),
    ("107", "LƠ MU JÔHANAN"),
    ("108", "Rơ Ông Rê Bê Ka"),
    ("109", "Trần Châu Khanh"),
    ("110", "Nguyễn Quốc Khánh"),
    ("111", "Nhal Khởi"),
    ("112", "Nguyễn Tuấn Kiệt"),
    ("113", "Kon Sơ K' Kornia"),
    ("114", "Pang Sim E Len"),
    ("115", "Nguyễn Hoàng Long"),
    ("116", "Nguyễn Duy Mạnh"),
    ("117", "Bon Dơng K' Trà My"),
    ("118", "K' Cil Ngọc"),
    ("119", "Liêng Klong Ha Phan"),
    ("120", "Nguyễn Trần Bảo Quyên"),
    ("121", "K' Mi Ra"),
    ("122", "Kon Sơ Ha Sàng"),
    ("123", "Bùi Đức Tài"),
    ("124", "Bon Dơng Li Tha"),
    ("125", "Trương Hữu Chí Thiện"),
    ("126", "Đinh Mạnh Tiến"),
    ("127", "Hồ Thị Thùy Trang"),
    ("128", "Nguyễn Thị Diệu Uyên"),
    ("129", "Rơ Ông Đa Vits"),
    ("130", "Bon Dơng K' Vy"),
    ("131", "Cil Đô Win"),
    ("132", "Học sinh 132"),
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            score INTEGER NOT NULL DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trash_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE NOT NULL,
            student_id TEXT NOT NULL,
            trash_type TEXT NOT NULL,
            points_added INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)

    for sid, full_name in STUDENTS_DATA:
        cur.execute("""
            INSERT INTO students (student_id, full_name, class_name, score)
            VALUES (?, ?, '9D', 0)
            ON CONFLICT(student_id) DO UPDATE SET
                full_name = excluded.full_name,
                class_name = excluded.class_name
        """, (sid, full_name))

    conn.commit()
    conn.close()
    print("Hoan tat cap nhat database.db voi danh sach 32 hoc sinh (101 - 132).")


if __name__ == "__main__":
    init_db()
