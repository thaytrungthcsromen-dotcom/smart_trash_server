import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from init_students import init_db

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

# Tự động khởi tạo và cập nhật danh sách học sinh khi server khởi động
init_db()

# Quy tắc cộng điểm theo loại rác
POINTS_RULE = {
    "tai_che": 5,
    "huu_co": 3,
    "vo_co": 2,
    "nguy_hai": 5,
}
VALID_TRASH_TYPES = set(POINTS_RULE.keys())


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/", methods=["GET"])
def dashboard():
    conn = get_db()
    students = conn.execute(
        "SELECT student_id, full_name, class_name, score FROM students ORDER BY CAST(student_id AS INTEGER)"
    ).fetchall()
    logs = conn.execute(
        """
        SELECT id, transaction_id, student_id, trash_type, points_added, created_at
        FROM trash_logs
        ORDER BY id DESC LIMIT 30
        """
    ).fetchall()
    conn.close()

    student_rows = "".join(
        f"<tr><td>{s['student_id']}</td><td>{s['full_name']}</td>"
        f"<td>{s['class_name']}</td><td><b>{s['score']}</b></td></tr>"
        for s in students
    )
    log_rows = "".join(
        f"<tr><td>{l['id']}</td><td>{l['transaction_id']}</td><td>{l['student_id']}</td>"
        f"<td>{l['trash_type']}</td><td>+{l['points_added']}</td><td>{l['created_at']}</td></tr>"
        for l in logs
    )

    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="utf-8">
        <title>Quản lý điểm rèn luyện - Thùng rác thông minh Edge AI</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 24px; background: #f4f6f9; }}
            h1, h2 {{ color: #1e293b; }}
            table {{ border-collapse: collapse; width: 100%; max-width: 900px; background: #fff; margin-bottom: 24px; }}
            th, td {{ border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left; }}
            th {{ background: #0f172a; color: #fff; }}
        </style>
    </head>
    <body>
        <h1>Bảng theo dõi điểm rèn luyện (Flask Server)</h1>
        <h2>Danh sách học sinh (101 - 132)</h2>
        <table>
            <tr><th>Mã HS</th><th>Họ tên</th><th>Lớp</th><th>Điểm</th></tr>
            {student_rows}
        </table>
        <h2>30 giao dịch gần nhất</h2>
        <table>
            <tr><th>#</th><th>Mã giao dịch</th><th>Mã HS</th><th>Loại rác</th><th>Điểm cộng</th><th>Thời gian</th></tr>
            {log_rows}
        </table>
    </body>
    </html>
    """


@app.route("/api/update_score", methods=["POST"])
def update_score():
    if not request.is_json:
        return jsonify({"ok": False, "error": "Request phải là JSON"}), 400

    payload = request.get_json(silent=True) or {}
    student_id = str(payload.get("student_id", "")).strip()
    trash_type = str(payload.get("trash_type", "")).strip()
    tx_id = str(payload.get("transaction_id", "")).strip()

    if not student_id.isdigit():
        return jsonify({"ok": False, "error": "Mã học sinh không hợp lệ"}), 400

    student_num = int(student_id)
    if student_num < 101 or student_num > 132:
        return jsonify({"ok": False, "error": "Mã học sinh ngoài phạm vi 101-132"}), 400

    if trash_type not in VALID_TRASH_TYPES:
        return jsonify({"ok": False, "error": "Loại rác không hợp lệ"}), 400

    if not tx_id:
        tx_id = f"fallback_{student_id}_{trash_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    points = POINTS_RULE[trash_type]

    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")

        student = conn.execute(
            "SELECT student_id, score FROM students WHERE student_id = ?",
            (student_id,),
        ).fetchone()
        if not student:
            conn.rollback()
            return jsonify({"ok": False, "error": "Không tìm thấy học sinh"}), 404

        dup = conn.execute(
            "SELECT id FROM trash_logs WHERE transaction_id = ?",
            (tx_id,),
        ).fetchone()
        if dup:
            conn.rollback()
            return jsonify({
                "ok": True,
                "duplicate": True,
                "message": "Giao dịch đã tồn tại, bỏ qua cộng trùng",
                "student_id": student_id,
                "total_score": student["score"],
            }), 200

        conn.execute(
            """
            INSERT INTO trash_logs (transaction_id, student_id, trash_type, points_added)
            VALUES (?, ?, ?, ?)
            """,
            (tx_id, student_id, trash_type, points),
        )
        conn.execute(
            "UPDATE students SET score = score + ? WHERE student_id = ?",
            (points, student_id),
        )
        updated = conn.execute(
            "SELECT score FROM students WHERE student_id = ?",
            (student_id,),
        ).fetchone()

        conn.commit()
        return jsonify({
            "ok": True,
            "duplicate": False,
            "message": "Cộng điểm thành công",
            "transaction_id": tx_id,
            "student_id": student_id,
            "trash_type": trash_type,
            "points_added": points,
            "total_score": updated["score"],
        }), 200

    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({"ok": True, "duplicate": True, "message": "Giao dịch trùng lặp"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"ok": False, "error": f"Lỗi server: {e}"}), 500
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
