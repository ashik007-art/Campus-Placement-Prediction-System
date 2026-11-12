"""Automated tests for routes, authentication, authorization, and workflows."""
import tempfile
import sqlite3
from pathlib import Path
import pytest
from app import create_app
from config import TestingConfig
from database.seed import seed_database
from utils.helpers import generate_csrf_token

@pytest.fixture
def test_app():
    """Create Flask application fixture configured with temporary test database."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp_path = tmp.name
    tmp.close()

    seed_database(tmp_path)

    class CustomTestConfig(TestingConfig):
        DATABASE_PATH = tmp_path
        WTF_CSRF_ENABLED = False

    app = create_app(CustomTestConfig)
    yield app

    try:
        Path(tmp_path).unlink(missing_ok=True)
    except Exception:
        pass

@pytest.fixture
def client(test_app):
    return test_app.test_client()

def test_homepage_public(client):
    """Verify landing page is reachable."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"PlacementHub" in response.data

def test_login_and_logout(client):
    """Verify login and session lifecycle for student and admin."""
    # 1. Invalid login
    with client.session_transaction() as sess:
        sess["_csrf_token"] = "valid_token"

    res = client.post("/login", data={
        "email": "invalid@campus.edu",
        "password": "WrongPassword",
        "csrf_token": "valid_token"
    }, follow_redirects=True)
    assert b"Invalid email address or password" in res.data

    # 2. Valid Admin Login
    res_admin = client.post("/login", data={
        "email": "admin@campus.edu",
        "password": "AdminSecurePass@2026",
        "csrf_token": "valid_token"
    }, follow_redirects=True)
    assert res_admin.status_code == 200
    assert b"Placement Officer Command Center" in res_admin.data

    # 3. Logout
    res_out = client.get("/logout", follow_redirects=True)
    assert b"logged out" in res_out.data

def test_student_registration_workflow(client):
    """Verify student registration and duplicate validation."""
    with client.session_transaction() as sess:
        sess["_csrf_token"] = "valid_token"

    new_email = "test.newstudent@campus.edu"
    res = client.post("/register", data={
        "full_name": "New Candidate",
        "email": new_email,
        "password": "Password123!",
        "confirm_password": "Password123!",
        "student_id_number": "STUNEW001",
        "department": "Computer Science & Engineering",
        "graduation_year": "2026",
        "phone": "+91 99999 11111",
        "csrf_token": "valid_token"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Registration successful" in res.data

    # Duplicate registration attempt
    res_dup = client.post("/register", data={
        "full_name": "Another Candidate",
        "email": new_email,
        "password": "Password123!",
        "confirm_password": "Password123!",
        "student_id_number": "STUNEW002",
        "department": "Information Technology",
        "graduation_year": "2026",
        "csrf_token": "valid_token"
    }, follow_redirects=True)
    assert b"already exists" in res_dup.data

def test_role_based_authorization(client):
    """Ensure non-admin cannot access administrative endpoints."""
    with client.session_transaction() as sess:
        sess["_csrf_token"] = "valid_token"

    # Log in as Priya Sharma (student)
    client.post("/login", data={
        "email": "priya.sharma@campus.edu",
        "password": "StudentPass@2026",
        "csrf_token": "valid_token"
    }, follow_redirects=True)

    # Student attempting to access admin students directory
    res_restricted = client.get("/students", follow_redirects=True)
    assert b"Access denied: Administrator privileges required" in res_restricted.data

def test_drives_and_companies_routes(client):
    """Verify drives and companies listings load properly."""
    with client.session_transaction() as sess:
        sess["_csrf_token"] = "valid_token"

    # Login as admin
    client.post("/login", data={
        "email": "admin@campus.edu",
        "password": "AdminSecurePass@2026",
        "csrf_token": "valid_token"
    }, follow_redirects=True)

    res_comp = client.get("/companies")
    assert res_comp.status_code == 200
    assert b"TechCorp Solutions" in res_comp.data

    res_drives = client.get("/drives")
    assert res_drives.status_code == 200
    assert b"TechCorp Annual Campus Drive 2026" in res_drives.data

def test_csv_export_endpoint(client):
    """Verify administrator CSV export generates valid CSV data."""
    with client.session_transaction() as sess:
        sess["_csrf_token"] = "valid_token"

    client.post("/login", data={
        "email": "admin@campus.edu",
        "password": "AdminSecurePass@2026",
        "csrf_token": "valid_token"
    }, follow_redirects=True)

    res = client.get("/reports/export-csv?type=departments")
    assert res.status_code == 200
    assert res.mimetype == "text/csv"
    assert b"Department,Total Students" in res.data

def test_student_profile_and_prediction_workflow(client):
    """Verify student profile view and readiness evaluation."""
    with client.session_transaction() as sess:
        sess["_csrf_token"] = "valid_token"

    client.post("/login", data={
        "email": "priya.sharma@campus.edu",
        "password": "StudentPass@2026",
        "csrf_token": "valid_token"
    }, follow_redirects=True)

    # Student viewing own profile
    res_prof = client.get("/students/1")
    assert res_prof.status_code == 200
    assert b"Priya Sharma" in res_prof.data

    with client.session_transaction() as sess:
        token = sess.get("_csrf_token")
        if not token:
            token = "valid_token"
            sess["_csrf_token"] = token

    # Evaluating readiness
    res_pred = client.post("/predictions/evaluate", data={
        "csrf_token": token
    }, follow_redirects=True)
    assert res_pred.status_code == 200
    assert b"Readiness Outcome" in res_pred.data
