"""Dashboard routes for Administrator and Student personas."""
from flask import Blueprint, render_template, redirect, url_for, session
from utils.helpers import login_required
from services.report_service import ReportService
from services.student_service import StudentService
from services.placement_service import PlacementService
from services.prediction_service import PredictionService
from services.recommendation_service import RecommendationService

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("index.html")

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    role = session.get("role")
    if role == "admin":
        metrics = ReportService.get_admin_dashboard_metrics()
        return render_template("dashboard/admin_dashboard.html", metrics=metrics)

    elif role == "student":
        student = StudentService.get_student_by_user_id(session["user_id"])
        if not student:
            return redirect(url_for("auth.logout"))

        # Synchronize session student_id
        session["student_id"] = student.id

        # Student-specific data
        latest_prediction = PredictionService.get_latest_prediction(student.id)
        recommendations = RecommendationService.get_student_recommendations(student.id)
        if not recommendations:
            recommendations = RecommendationService.generate_recommendations_for_student(student.id)

        applications = PlacementService.get_student_applications(student.id)
        upcoming_drives = PlacementService.get_all_drives(status="Upcoming")

        return render_template(
            "dashboard/student_dashboard.html",
            student=student,
            latest_prediction=latest_prediction,
            recommendations=recommendations[:4],
            applications=applications,
            upcoming_drives=upcoming_drives[:4]
        )

    return redirect(url_for("auth.login"))
