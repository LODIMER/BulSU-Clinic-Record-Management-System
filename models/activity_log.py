from models.database import get_db


class ActivityLogModel:
    @staticmethod
    def log(user_id, activity, record_affected=""):
        conn = get_db()
        conn.execute(
            """
            INSERT INTO activity_logs (user_id, activity, record_affected)
            VALUES (?, ?, ?)
            """,
            (user_id, activity, record_affected),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_all(limit=50):
        conn = get_db()
        rows = conn.execute(
            """
            SELECT al.*, u.username
            FROM activity_logs al
            LEFT JOIN users u ON al.user_id = u.id
            ORDER BY al.created_at DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_user(user_id, limit=20):
        conn = get_db()
        rows = conn.execute(
            """
            SELECT * FROM activity_logs
            WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]
