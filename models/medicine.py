from datetime import date

from config import Config
from models.database import get_db


class MedicineModel:
    @staticmethod
    def create(data):
        conn = get_db()
        cursor = conn.execute(
            """
            INSERT INTO medicines (name, category, quantity, expiration_date)
            VALUES (?, ?, ?, ?)
            """,
            (
                data["name"],
                data.get("category", ""),
                int(data.get("quantity", 0)),
                data.get("expiration_date", ""),
            ),
        )
        conn.commit()
        medicine_id = cursor.lastrowid
        conn.close()
        return medicine_id

    @staticmethod
    def get_by_id(medicine_id):
        conn = get_db()
        row = conn.execute("SELECT * FROM medicines WHERE id = ?", (medicine_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all():
        conn = get_db()
        rows = conn.execute("SELECT * FROM medicines ORDER BY name").fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def update(medicine_id, data):
        conn = get_db()
        conn.execute(
            """
            UPDATE medicines SET name = ?, category = ?, quantity = ?,
            expiration_date = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
            """,
            (
                data["name"],
                data.get("category", ""),
                int(data.get("quantity", 0)),
                data.get("expiration_date", ""),
                medicine_id,
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(medicine_id):
        conn = get_db()
        conn.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def release(visit_id, medicine_id, quantity):
        conn = get_db()
        medicine = conn.execute(
            "SELECT quantity FROM medicines WHERE id = ?", (medicine_id,)
        ).fetchone()
        if not medicine or medicine["quantity"] < quantity:
            conn.close()
            return False

        conn.execute(
            """
            INSERT INTO medicine_releases (visit_id, medicine_id, quantity)
            VALUES (?, ?, ?)
            """,
            (visit_id, medicine_id, quantity),
        )
        conn.execute(
            "UPDATE medicines SET quantity = quantity - ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (quantity, medicine_id),
        )
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_low_stock():
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM medicines WHERE quantity <= ? ORDER BY quantity",
            (Config.LOW_STOCK_THRESHOLD,),
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_expired():
        conn = get_db()
        today = date.today().isoformat()
        rows = conn.execute(
            """
            SELECT * FROM medicines
            WHERE expiration_date != '' AND expiration_date < ?
            ORDER BY expiration_date
            """,
            (today,),
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def usage_summary():
        conn = get_db()
        rows = conn.execute(
            """
            SELECT m.name, m.category, COALESCE(SUM(mr.quantity), 0) as total_released
            FROM medicines m
            LEFT JOIN medicine_releases mr ON m.id = mr.medicine_id
            GROUP BY m.id ORDER BY total_released DESC
            """
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]
