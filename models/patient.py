from models.database import get_db


class PatientModel:
    @staticmethod
    def create(data, user_id=None):
        conn = get_db()
        cursor = conn.execute(
            """
            INSERT INTO patients (
                user_id, student_id, first_name, last_name, course, year_level,
                contact_number, emergency_contact, medical_history, allergies
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                data["student_id"],
                data["first_name"],
                data["last_name"],
                data.get("course", ""),
                data.get("year_level", ""),
                data.get("contact_number", ""),
                data.get("emergency_contact", ""),
                data.get("medical_history", ""),
                data.get("allergies", ""),
            ),
        )
        conn.commit()
        patient_id = cursor.lastrowid
        conn.close()
        return patient_id

    @staticmethod
    def get_by_id(patient_id):
        conn = get_db()
        row = conn.execute(
            """
            SELECT p.*, u.username
            FROM patients p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.id = ?
            """,
            (patient_id,),
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_user_id(user_id):
        conn = get_db()
        row = conn.execute("SELECT * FROM patients WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all(search=""):
        conn = get_db()
        query = """
            SELECT p.*, u.username
            FROM patients p
            LEFT JOIN users u ON p.user_id = u.id
        """
        params = []
        if search:
            query += """
                WHERE p.student_id LIKE ? OR p.first_name LIKE ?
                OR p.last_name LIKE ? OR p.course LIKE ?
            """
            term = f"%{search}%"
            params = [term, term, term, term]
        query += " ORDER BY p.last_name, p.first_name"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def update(patient_id, data):
        conn = get_db()
        conn.execute(
            """
            UPDATE patients SET
                student_id = ?, first_name = ?, last_name = ?, course = ?,
                year_level = ?, contact_number = ?, emergency_contact = ?,
                medical_history = ?, allergies = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                data["student_id"],
                data["first_name"],
                data["last_name"],
                data.get("course", ""),
                data.get("year_level", ""),
                data.get("contact_number", ""),
                data.get("emergency_contact", ""),
                data.get("medical_history", ""),
                data.get("allergies", ""),
                patient_id,
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_student_id(student_id):
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM patients WHERE student_id = ?", (student_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def find_or_update_from_form(data):
        """Find patient by student ID or create a new record without a login account."""
        existing = PatientModel.get_by_student_id(data["student_id"])
        if existing:
            PatientModel.update(existing["id"], data)
            return existing["id"]
        return PatientModel.create(data)

    @staticmethod
    def count():
        conn = get_db()
        count = conn.execute("SELECT COUNT(*) as total FROM patients").fetchone()["total"]
        conn.close()
        return count

    @staticmethod
    def import_rows(rows, update_existing=False):
        """Import patient rows from Google Form CSV. Returns stats dict."""
        imported = 0
        updated = 0
        skipped = 0
        errors = []

        for row in rows:
            data = {k: v for k, v in row.items() if not k.startswith("_")}
            student_id = data.get("student_id", "").strip()

            if not student_id:
                if data.get("first_name") or data.get("last_name"):
                    name_part = f"{data.get('first_name', '')}{data.get('last_name', '')}"
                    student_id = f"GF-{abs(hash(name_part)) % 100000:05d}"
                    data["student_id"] = student_id
                else:
                    skipped += 1
                    errors.append(f"Row {row.get('_line', '?')}: no identifiable data.")
                    continue

            existing = PatientModel.get_by_student_id(student_id)
            if existing:
                if update_existing:
                    PatientModel.update(existing["id"], data)
                    updated += 1
                else:
                    skipped += 1
            else:
                PatientModel.create(data)
                imported += 1

        return {
            "imported": imported,
            "updated": updated,
            "skipped": skipped,
            "errors": errors,
        }
