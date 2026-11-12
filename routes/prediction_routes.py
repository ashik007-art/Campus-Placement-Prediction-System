"""Placement readiness prediction and assessment routes."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from utils.helpers import login_required, verify_csrf_token
from services.prediction_service import PredictionService
from services.student_service import StudentService
from services.recommendation_service import RecommendationService

prediction_bp = Blueprint("predictions", __name__)

@prediction_bp.route("/predictions")
@login_required
def list_predictions():
    role = session.get("role")
    if role == "student":
        student_id = session.get("student_id")
        student = StudentService.get_student_by_id(student_id)
        predictions = PredictionService.get_student_predictions(student_id)
        latest_pred = predictions[0] if predictions else None
        return render_template(
            "predictions/prediction_form.html",
            student=student,
            predictions=predictions,
            latest_prediction=latest_pred
        )
    elif role == "admin":
        student_id = request.args.get("student_id")
        if student_id:
            student = StudentService.get_student_by_id(int(student_id))
            predictions = PredictionService.get_student_predictions(int(student_id))
            return render_template("predictions/prediction_form.html", student=student, predictions=predictions, is_admin=True)
        else:
            all_predictions = PredictionService.get_all_predictions()
            students = StudentService.get_all_students()
            return render_template("predictions/prediction_form.html", all_predictions=all_predictions, students=students, is_admin=True)

@prediction_bp.route("/predictions/evaluate", methods=["POST"])
@login_required
def evaluate_readiness():
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Security token expired.", "danger")
        return redirect(url_for("predictions.list_predictions"))

    role = session.get("role")
    if role == "student":
        student_id = session.get("student_id")
    elif role == "admin":
        student_id = request.form.get("student_id")
        if not student_id:
            flash("Please select a student to evaluate.", "warning")
            return redirect(url_for("predictions.list_predictions"))
        student_id = int(student_id)
    else:
        abort(403)

    result, err = PredictionService.run_and_save_prediction(student_id)
    if err:
        flash(err, "danger")
        return redirect(url_for("predictions.list_predictions"))

    return render_template(
        "predictions/prediction_result.html",
        result=result,
        student=result["student"],
        recommendations=result["recommendations"]
    )
