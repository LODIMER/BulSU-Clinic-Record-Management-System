from werkzeug.security import check_password_hash, generate_password_hash

from models.database import get_db


class UserModel:
    @staticmethod
    def create(username, password, role):
        conn = get_db()
        hashed = generate_password_hash(password)
        cursor = conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed, role),
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id

    @staticmethod
    def authenticate(username, password):
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username,),
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            return dict(user)
        return None

    @staticmethod
    def get_by_id(user_id):
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def get_all_staff():
        conn = get_db()
        rows = conn.execute(
            "SELECT id, username, role, is_active, created_at FROM users WHERE role = 'staff'"
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def reset_password(user_id, new_password):
        conn = get_db()
        hashed = generate_password_hash(new_password)
        conn.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
        conn.commit()
        conn.close()

    @staticmethod
    def toggle_active(user_id, is_active):
        conn = get_db()
        conn.execute(
            "UPDATE users SET is_active = ? WHERE id = ?", (1 if is_active else 0, user_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(user_id):
        conn = get_db()
        conn.execute("DELETE FROM users WHERE id = ? AND role = 'staff'", (user_id,))
        conn.commit()
        conn.close()
