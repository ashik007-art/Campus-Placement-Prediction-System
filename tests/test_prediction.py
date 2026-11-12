"""Automated tests for feature transformation, inference engine, demo scoring, and recommendations."""
import tempfile
import sqlite3
from pathlib import Path
import pytest
from prediction.preprocessing import extract_features_from_student, FEATURE_COLUMNS
from prediction.predictor import calculate_demo_readiness, predict_placement, get_category_from_score
from services.recommendation_service import RecommendationService
from database.seed import seed_database

@pytest.fixture
def temp_db():
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

def test_feature_extraction():
    """Verify feature extractor builds aligned DataFrame."""
    student_payload = {
        "tenth_percentage": 85.0,
        "twelfth_percentage": 82.5,
        "cgpa": 8.1,
        "backlogs": 0,
        "attendance_percentage": 92.0,
        "communication_level": "Advanced",
        "aptitude_level": "Intermediate",
        "internship_count": 1,
        "project_count": 2,
        "certification_count": 1,
        "skill_count": 4
    }
    df = extract_features_from_student(student_payload)
    assert list(df.columns) == FEATURE_COLUMNS
    assert len(df) == 1
    assert df["cgpa"].iloc[0] == 8.1
    assert df["communication_score"].iloc[0] == 3

def test_demo_readiness_scoring():
    """Verify transparent rule-based demo scoring behavior and bounds."""
    # Strong student
    high_student = {
        "tenth_percentage": 90.0,
        "twelfth_percentage": 90.0,
        "cgpa": 9.2,
        "backlogs": 0,
        "attendance_percentage": 95.0,
        "communication_level": "Advanced",
        "aptitude_level": "Advanced",
        "skills": ["Python", "Java", "SQL", "ML"],
        "projects": [{"title": "P1"}, {"title": "P2"}],
        "internships": [{"company": "C1"}]
    }
    res_high = calculate_demo_readiness(high_student)
    assert res_high["mode"] == "Demo Readiness Score"
    assert res_high["readiness_score"] >= 75.0
    assert res_high["readiness_category"] == "High Readiness"

    # Weak student with backlogs
    low_student = {
        "tenth_percentage": 60.0,
        "twelfth_percentage": 58.0,
        "cgpa": 5.8,
        "backlogs": 3,
        "attendance_percentage": 65.0,
        "communication_level": "Beginner",
        "aptitude_level": "Beginner",
        "skills": [],
        "projects": [],
        "internships": []
    }
    res_low = calculate_demo_readiness(low_student)
    assert res_low["readiness_score"] < 55.0
    assert res_low["readiness_category"] == "Needs Improvement"
    assert "backlogs" in res_low["key_factors"].lower()

def test_missing_model_fallback():
    """Ensure predictor gracefully falls back to Demo Readiness Score if model file is missing."""
    student_payload = {
        "tenth_percentage": 80.0,
        "twelfth_percentage": 80.0,
        "cgpa": 7.5,
        "backlogs": 0,
        "attendance_percentage": 85.0
    }
    # Point to nonexistent model path
    res = predict_placement(student_payload, model_path="nonexistent_model.joblib", preprocessor_path="nonexistent_prep.joblib")
    assert res["mode"] == "Demo Readiness Score"
    assert "readiness_score" in res
    assert res["readiness_category"] in ("High Readiness", "Moderate Readiness", "Needs Improvement")

def test_skill_gap_division_by_zero_handling(monkeypatch, temp_db):
    """Ensure skill gap analysis handles job roles with 0 required skills safely."""
    conn, tmp_path = temp_db
    monkeypatch.setenv("DATABASE_PATH", tmp_path)

    # Insert a dummy job role with zero required skills
    cur = conn.cursor()
    cur.execute("SELECT id FROM companies LIMIT 1")
    cid = cur.fetchone()["id"]
    cur.execute("""
        INSERT INTO job_roles (company_id, role_name, min_cgpa, max_backlogs, salary_package)
        VALUES (?, 'Zero Skill Role', 6.0, 0, '5.0 LPA')
    """, (cid,))
    role_id = cur.lastrowid
    conn.commit()

    cur.execute("SELECT id FROM students LIMIT 1")
    sid = cur.fetchone()["id"]

    from app import create_app
    from config import TestingConfig

    class TestCfg(TestingConfig):
        DATABASE_PATH = tmp_path

    app = create_app(TestCfg)
    with app.app_context():
        gap = RecommendationService.analyze_skill_gap(sid, job_role_id=role_id)
        assert gap["total_required"] == 0
        assert gap["match_percentage"] == 100.0  # Safe no division error
        assert len(gap["missing_skills"]) == 0

def test_recommendation_generation(monkeypatch, temp_db):
    """Ensure rule-based recommendation generator creates relevant recommendations for backlogs and skills."""
    conn, tmp_path = temp_db
    monkeypatch.setenv("DATABASE_PATH", tmp_path)

    from app import create_app
    from config import TestingConfig

    class TestCfg(TestingConfig):
        DATABASE_PATH = tmp_path

    app = create_app(TestCfg)
    with app.app_context():
        # Candidate 3 (Ananya Patel has 2 backlogs in seed)
        cur = conn.cursor()
        cur.execute("SELECT id FROM students WHERE student_id_number = 'STU2026003'")
        row = cur.fetchone()
        sid = row["id"]

        recs = RecommendationService.generate_recommendations_for_student(sid)
        assert len(recs) > 0
        titles = [r.title for r in recs]
        # Must recommend clearing backlogs with High priority
        assert any("backlog" in t.lower() for t in titles)
        backlog_rec = [r for r in recs if "backlog" in r.title.lower()][0]
        assert backlog_rec.priority == "High"
