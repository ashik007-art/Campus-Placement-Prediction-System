"""Recommendations and Skill Gap Analysis routes."""
from flask import Blueprint, render_template, request, session, jsonify, flash, redirect, url_for
from utils.helpers import login_required
from services.student_service import StudentService
from services.company_service import CompanyService
from services.placement_service import PlacementService
from services.recommendation_service import RecommendationService

recommendation_bp = Blueprint("recommendations", __name__)

@recommendation_bp.route("/recommendations")
@login_required
def recommendations():
    role = session.get("role")
    if role == "student":
        student_id = session.get("student_id")
    else:
        student_id = request.args.get("student_id")
        if not student_id:
            # Pick first student for demonstration if admin
            students = StudentService.get_all_students()
            student_id = students[0].id if students else None
        else:
            student_id = int(student_id)

    if not student_id:
        flash("No student profile available for recommendation review.", "warning")
        return redirect(url_for("dashboard.dashboard"))

    student = StudentService.get_student_by_id(student_id)
    recs = RecommendationService.get_student_recommendations(student_id)
    if not recs:
        recs = RecommendationService.generate_recommendations_for_student(student_id)

    # Job roles for skill gap comparison
    companies = CompanyService.get_all_companies()
    all_job_roles = []
    for c in companies:
        for r in c.job_roles:
            all_job_roles.append(r)

    # Check if target role was selected in request
    selected_role_id = request.args.get("job_role_id")
    skill_gap_result = None
    if selected_role_id:
        skill_gap_result = RecommendationService.analyze_skill_gap(student_id, job_role_id=int(selected_role_id))

    return render_template(
        "recommendations/recommendations.html",
        student=student,
        recommendations=recs,
        job_roles=all_job_roles,
        selected_role_id=int(selected_role_id) if selected_role_id else None,
        skill_gap=skill_gap_result
    )

@recommendation_bp.route("/recommendations/skill-gap-api")
@login_required
def skill_gap_api():
    student_id = request.args.get("student_id") or session.get("student_id")
    job_role_id = request.args.get("job_role_id")
    drive_id = request.args.get("drive_id")

    if not student_id:
        return jsonify({"error": "student_id is required"}), 400

    analysis = RecommendationService.analyze_skill_gap(
        int(student_id),
        job_role_id=int(job_role_id) if job_role_id else None,
        drive_id=int(drive_id) if drive_id else None
    )
    return jsonify(analysis)
