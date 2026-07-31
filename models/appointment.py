from datetime import date

from models.database import get_db


class AppointmentModel:
    @staticmethod
    def create(patient_id, data):
        conn = get_db()
        cursor = conn.execute(
            """
            INSERT INTO appointments (patient_id, appointment_date, appointment_time, reason)
            VALUES (?, ?, ?, ?)
            """,
            (
                patient_id,
                data["appointment_date"],
                data["appointment_time"],
                data["reason"],
            ),
        )
        conn.commit()
        appointment_id = cursor.lastrowid
        conn.close()
        return appointment_id

    @staticmethod
    def get_by_id(appointment_id):
        conn = get_db()
        row = conn.execute(
            """
            SELECT a.*, p.student_id, p.first_name, p.last_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.id = ?
            """,
            (appointment_id,),
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all(search="", status=""):
        conn = get_db()
        query = """
            SELECT a.*, p.student_id, p.first_name, p.last_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE 1=1
        """
        params = []
        if search:
            query += """
                AND (p.student_id LIKE ? OR p.first_name LIKE ?
                OR p.last_name LIKE ? OR a.reason LIKE ?)
            """
            term = f"%{search}%"
            params.extend([term, term, term, term])
        if status:
            query += " AND a.status = ?"
            params.append(status)
        query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_patient(patient_id):
        conn = get_db()
        rows = conn.execute(
            """
            SELECT * FROM appointments
            WHERE patient_id = ?
            ORDER BY appointment_date DESC, appointment_time DESC
            """,
            (patient_id,),
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_today_count():
        conn = get_db()
        today = date.today().isoformat()
        count = conn.execute(
            """
            SELECT COUNT(*) as total FROM appointments
            WHERE appointment_date = ? AND status IN ('pending', 'approved')
            """,
            (today,),
        ).fetchone()["total"]
        conn.close()
        return count

    @staticmethod
    def update_status(appointment_id, status, staff_notes=None):
        conn = get_db()
        conn.execute(
            """
            UPDATE appointments SET status = ?, staff_notes = ?,
            updated_at = CURRENT_TIMESTAMP WHERE id = ?
            """,
            (status, staff_notes, appointment_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def reschedule(appointment_id, appointment_date, appointment_time):
        conn = get_db()
        conn.execute(
            """
            UPDATE appointments SET appointment_date = ?, appointment_time = ?,
            updated_at = CURRENT_TIMESTAMP WHERE id = ?
            """,
            (appointment_date, appointment_time, appointment_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def status_summary():
        conn = get_db()
        rows = conn.execute(
            """
            SELECT status, COUNT(*) as count
            FROM appointments GROUP BY status
            """
        ).fetchall()
        conn.close()
        return {row["status"]: row["count"] for row in rows}
