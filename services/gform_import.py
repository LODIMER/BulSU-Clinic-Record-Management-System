import csv
import io
import re
from typing import Any


# Common Google Form / Sheets column headers (case-insensitive)
FIELD_ALIASES = {
    "student_id": [
        "student id",
        "student_id",
        "student number",
        "id number",
        "id no",
        "student no",
    ],
    "first_name": ["first name", "firstname", "given name"],
    "last_name": ["last name", "lastname", "surname", "family name"],
    "full_name": ["full name", "name", "complete name", "student name"],
    "course": ["course", "program", "course/program", "course / program", "course program"],
    "year_level": ["year level", "year_level", "year", "level", "year level "],
    "contact_number": [
        "contact number",
        "contact",
        "phone",
        "mobile number",
        "cellphone",
        "phone number",
    ],
    "emergency_contact": [
        "emergency contact",
        "emergency",
        "guardian contact",
        "emergency contact person",
    ],
    "medical_history": [
        "medical history",
        "history",
        "past medical history",
        "medical background",
    ],
    "allergies": ["allergies", "allergy", "known allergies", "food/drug allergies"],
}

SKIP_COLUMNS = {"timestamp", "email address", "email", "score", "grade"}


def _normalize_header(header: str) -> str:
    return re.sub(r"\s+", " ", header.strip().lower())


def _match_field(header: str) -> str | None:
    normalized = _normalize_header(header)
    if normalized in SKIP_COLUMNS:
        return None
    for field, aliases in FIELD_ALIASES.items():
        if normalized in aliases:
            return field
    return None


def _split_full_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split(None, 1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def build_column_map(headers: list[str]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for index, header in enumerate(headers):
        field = _match_field(header)
        if field and field not in mapping:
            mapping[field] = index
    return mapping


def parse_gform_csv(file_content: bytes) -> dict[str, Any]:
    """Parse a Google Form CSV export and map rows to patient records."""
    text = file_content.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text))

    try:
        headers = next(reader)
    except StopIteration:
        return {"rows": [], "mapping": {}, "headers": [], "errors": ["CSV file is empty."]}

    column_map = build_column_map(headers)
    errors: list[str] = []

    if "student_id" not in column_map and "full_name" not in column_map:
        errors.append(
            "Could not find Student ID or Full Name column. "
            "Export your Google Form responses to CSV and try again."
        )

    rows: list[dict[str, str]] = []
    for line_num, row in enumerate(reader, start=2):
        if not any(cell.strip() for cell in row):
            continue

        record: dict[str, str] = {
            "student_id": "",
            "first_name": "",
            "last_name": "",
            "course": "",
            "year_level": "",
            "contact_number": "",
            "emergency_contact": "",
            "medical_history": "",
            "allergies": "",
            "_line": str(line_num),
        }

        for field, index in column_map.items():
            if field == "full_name":
                continue
            if index < len(row):
                record[field] = row[index].strip()

        if "full_name" in column_map:
            index = column_map["full_name"]
            if index < len(row) and row[index].strip():
                first, last = _split_full_name(row[index])
                if not record["first_name"]:
                    record["first_name"] = first
                if not record["last_name"]:
                    record["last_name"] = last

        if not record["student_id"] and not (record["first_name"] or record["last_name"]):
            errors.append(f"Row {line_num}: missing student ID and name — skipped.")
            continue

        rows.append(record)

    return {
        "rows": rows,
        "mapping": column_map,
        "headers": headers,
        "errors": errors,
    }
