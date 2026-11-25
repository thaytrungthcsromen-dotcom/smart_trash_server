import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")


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

    for num in range(101, 133):
        sid = str(num)
        cur.execute("""
            INSERT OR IGNORE INTO students (student_id, full_name, class_name, score)
            VALUES (?, ?, ?, 0)
        """, (sid, f"Học sinh {sid}", "9D"))

    conn.commit()
    conn.close()
    print("Hoan tat tao database.db voi danh sach ma 101 - 132.")


if __name__ == "__main__":
    init_db()