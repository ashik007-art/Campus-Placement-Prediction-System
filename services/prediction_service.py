"""Prediction orchestrator and persistence service."""
from database.db import get_db, query_db, execute_db
from models.prediction import PredictionRecord
from prediction.predictor import predict_placement
from services.student_service import StudentService
from services.recommendation_service import RecommendationService

class PredictionService:

    @staticmethod
    def run_and_save_prediction(student_id):
        """
        Executes placement readiness evaluation, records the result in the database,
        triggers updated recommendations, and returns full assessment details.
        """
        student = StudentService.get_student_by_id(student_id)
        if not student:
            return None, "Student not found."

        # Prepare payload dictionary for predictor
        student_data = student.to_dict()
        student_data["skills"] = student.skills
        student_data["projects"] = student.projects
        student_data["internships"] = student.internships
        student_data["certifications"] = student.certifications

        # Run predictor
        result = predict_placement(student_data)

        # Persist prediction record
        db = get_db()
        cur = db.execute("""
            INSERT INTO predictions (student_id, mode, readiness_score, readiness_category, key_factors)
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, result["mode"], result["readiness_score"], result["readiness_category"], result["key_factors"]))
        pred_id = cur.lastrowid
        db.commit()

        # Generate fresh recommendations aligned with gaps
        recommendations = RecommendationService.generate_recommendations_for_student(student_id)

        # Retrieve saved prediction entity
        saved_row = query_db("""
            SELECT p.*, u.full_name as student_name
            FROM predictions p
            JOIN students s ON p.student_id = s.id
            JOIN users u ON s.user_id = u.id
            WHERE p.id = ?
        """, (pred_id,), one=True)

        record = PredictionRecord(dict(saved_row))
        result["record"] = record
        result["recommendations"] = recommendations
        result["student"] = student

        return result, ""

    @staticmethod
    def get_student_predictions(student_id):
        rows = query_db("""
            SELECT p.*, u.full_name as student_name
            FROM predictions p
            JOIN students s ON p.student_id = s.id
            JOIN users u ON s.user_id = u.id
            WHERE p.student_id = ?
            ORDER BY p.created_at DESC
        """, (student_id,))
        return [PredictionRecord(dict(r)) for r in rows]

    @staticmethod
    def get_latest_prediction(student_id):
        row = query_db("""
            SELECT p.*, u.full_name as student_name
            FROM predictions p
            JOIN students s ON p.student_id = s.id
            JOIN users u ON s.user_id = u.id
            WHERE p.student_id = ?
            ORDER BY p.created_at DESC
            LIMIT 1
        """, (student_id,), one=True)
        return PredictionRecord(dict(row)) if row else None

    @staticmethod
    def get_all_predictions(limit=100):
        rows = query_db("""
            SELECT p.*, u.full_name as student_name, s.student_id_number, s.department
            FROM predictions p
            JOIN students s ON p.student_id = s.id
            JOIN users u ON s.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(r) for r in rows]
