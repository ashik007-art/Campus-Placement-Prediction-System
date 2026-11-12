"""Automated tests for database schema, constraints, foreign keys, and transactions."""
import tempfile
import sqlite3
from pathlib import Path
import pytest
from database.seed import seed_database

@pytest.fixture
def temp_db():
    """Create a temporary database file for test isolation."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp_path = tmp.name
    tmp.close()

    seed_database(tmp_path)
    conn = sqlite3.connect(tmp_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row

    yield conn, tmp_path

    conn.close()
    try:
        Path(tmp_path).unlink(missing_ok=True)
    except Exception:
        pass

def test_database_foreign_key_enforcement(temp_db):
    """Verify that foreign keys are enforced and reject orphan rows."""
    conn, _ = temp_db
    # Attempting to insert an academic record for non-existent student_id 99999
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("""
            INSERT INTO academic_details (student_id, tenth_percentage, twelfth_percentage, cgpa, backlogs, attendance_percentage)
            VALUES (99999, 85.0, 85.0, 8.5, 0, 90.0)
        """)

def test_user_cascade_deletion(temp_db):
    """Verify that deleting a user account cascades to the student record and academics."""
    conn, _ = temp_db
    # Find user Priya Sharma
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = 'priya.sharma@campus.edu'")
    user_row = cur.fetchone()
    assert user_row is not None
    user_id = user_row["id"]

    cur.execute("SELECT id FROM students WHERE user_id = ?", (user_id,))
    student_row = cur.fetchone()
    assert student_row is not None
    student_id = student_row["id"]

    # Delete user
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()

    # Check student is gone
    cur.execute("SELECT id FROM students WHERE id = ?", (student_id,))
    assert cur.fetchone() is None

    # Check academic details are gone
    cur.execute("SELECT id FROM academic_details WHERE student_id = ?", (student_id,))
    assert cur.fetchone() is None

def test_duplicate_application_prevention(temp_db):
    """Verify unique constraint prevents duplicate applications for the same drive and student."""
    conn, _ = temp_db
    cur = conn.cursor()
    cur.execute("SELECT drive_id, student_id FROM applications LIMIT 1")
    app = cur.fetchone()
    assert app is not None

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO applications (drive_id, student_id, status) VALUES (?, ?, 'Applied')",
            (app["drive_id"], app["student_id"])
        )

def test_academic_constraints(temp_db):
    """Verify range constraints on CGPA and percentages."""
    conn, _ = temp_db
    cur = conn.cursor()
    cur.execute("SELECT id FROM students LIMIT 1")
    student = cur.fetchone()

    # CGPA > 10 must fail CHECK constraint
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("""
            INSERT INTO academic_details (student_id, tenth_percentage, twelfth_percentage, cgpa, backlogs, attendance_percentage)
            VALUES (?, 80.0, 80.0, 11.5, 0, 85.0)
        """, (student["id"] + 100,))
