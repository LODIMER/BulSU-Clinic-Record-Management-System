from datetime import date

from models.database import get_db


class ClinicVisitModel:
    @staticmethod
    def create(data, staff_id):
        conn = get_db()
        cursor = conn.execute(
            """
            INSERT INTO clinic_visits (
                patient_id, staff_id, visit_date, visit_time, reason,
                vital_signs, assessment, treatment, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["patient_id"],
                staff_id,
                data["visit_date"],
                data["visit_time"],
                data["reason"],
                data.get("vital_signs", ""),
                data.get("assessment", ""),
                data.get("treatment", ""),
                data.get("notes", ""),
            ),
        )
        conn.commit()
        visit_id = cursor.lastrowid
        conn.close()
        return visit_id

    @staticmethod
    def get_by_id(visit_id):
        conn = get_db()
        row = conn.execute(
            """
            SELECT v.*, p.student_id, p.first_name, p.last_name,
                   u.username as staff_username
            FROM clinic_visits v
            JOIN patients p ON v.patient_id = p.id
            LEFT JOIN users u ON v.staff_id = u.id
            WHERE v.id = ?
            """,
            (visit_id,),
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all(search=""):
        conn = get_db()
        query = """
            SELECT v.*, p.student_id, p.first_name, p.last_name
            FROM clinic_visits v
            JOIN patients p ON v.patient_id = p.id
        """
        params = []
        if search:
            query += """
                WHERE p.student_id LIKE ? OR p.first_name LIKE ?
                OR p.last_name LIKE ? OR v.reason LIKE ?
            """
            term = f"%{search}%"
            params = [term, term, term, term]
        query += " ORDER BY v.visit_date DESC, v.visit_time DESC"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_patient(patient_id):
        conn = get_db()
        rows = conn.execute(
            """
            SELECT v.*, u.username as staff_username
            FROM clinic_visits v
            LEFT JOIN users u ON v.staff_id = u.id
            WHERE v.patient_id = ?
            ORDER BY v.visit_date DESC, v.visit_time DESC
            """,
            (patient_id,),
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_recent(limit=10):
        conn = get_db()
        rows = conn.execute(
            """
            SELECT v.*, p.student_id, p.first_name, p.last_name
            FROM clinic_visits v
            JOIN patients p ON v.patient_id = p.id
            ORDER BY v.created_at DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def count():
        conn = get_db()
        count = conn.execute("SELECT COUNT(*) as total FROM clinic_visits").fetchone()["total"]
        conn.close()
        return count

    @staticmethod
    def common_reasons(limit=5):
        conn = get_db()
        rows = conn.execute(
            """
            SELECT reason, COUNT(*) as count
            FROM clinic_visits GROUP BY reason
            ORDER BY count DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_medicines_for_visit(visit_id):
        conn = get_db()
        rows = conn.execute(
            """
            SELECT mr.*, m.name, m.category
            FROM medicine_releases mr
            JOIN medicines m ON mr.medicine_id = m.id
            WHERE mr.visit_id = ?
            """,
            (visit_id,),
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]
