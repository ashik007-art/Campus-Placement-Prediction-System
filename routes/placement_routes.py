"""Placement drives and student applications management routes."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from utils.helpers import login_required, admin_required, student_required, verify_csrf_token
from services.placement_service import PlacementService
from services.company_service import CompanyService
from services.student_service import StudentService

placement_bp = Blueprint("placements", __name__)

@placement_bp.route("/drives")
@login_required
def list_drives():
    status = request.args.get("status")
    company_id = request.args.get("company_id")
    drives = PlacementService.get_all_drives(status=status, company_id=company_id)
    companies = CompanyService.get_all_companies()

    # If student, collect set of applied drive IDs
    applied_drive_ids = set()
    student = None
    if session.get("role") == "student" and session.get("student_id"):
        student = StudentService.get_student_by_id(session["student_id"])
        apps = PlacementService.get_student_applications(session["student_id"])
        applied_drive_ids = {a.drive_id for a in apps}

    return render_template(
        "placements/drives.html",
        drives=drives,
        companies=companies,
        selected_status=status,
        selected_company_id=company_id,
        applied_drive_ids=applied_drive_ids,
        student=student
    )

@placement_bp.route("/drives/add", methods=["GET", "POST"])
@admin_required
def add_drive():
    companies = CompanyService.get_all_companies()
    if request.method == "POST":
        if not verify_csrf_token(request.form.get("csrf_token")):
            flash("Session token expired.", "danger")
            return redirect(url_for("placements.add_drive"))

        company_id = request.form.get("company_id")
        job_role_id = request.form.get("job_role_id")
        title = request.form.get("title", "").strip()
        drive_date = request.form.get("drive_date")
        application_deadline = request.form.get("application_deadline")
        selection_process = request.form.get("selection_process", "").strip()
        status = request.form.get("status", "Upcoming")

        if not all([company_id, job_role_id, title, drive_date, application_deadline]):
            flash("All mandatory fields must be completed.", "warning")
            return render_template("placements/drive_form.html", companies=companies, drive=None)

        success, res = PlacementService.create_drive(
            company_id=int(company_id),
            job_role_id=int(job_role_id),
            title=title,
            drive_date=drive_date,
            application_deadline=application_deadline,
            selection_process=selection_process,
            status=status
        )

        if success:
            flash("Placement drive created successfully.", "success")
            return redirect(url_for("placements.list_drives"))
        else:
            flash(res, "danger")

    return render_template("placements/drive_form.html", companies=companies, drive=None)

@placement_bp.route("/drives/<int:drive_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_drive(drive_id):
    drive = PlacementService.get_drive_by_id(drive_id)
    if not drive:
        flash("Drive not found.", "warning")
        return redirect(url_for("placements.list_drives"))

    companies = CompanyService.get_all_companies()
    if request.method == "POST":
        if not verify_csrf_token(request.form.get("csrf_token")):
            flash("Session token expired.", "danger")
            return redirect(url_for("placements.edit_drive", drive_id=drive_id))

        company_id = request.form.get("company_id")
        job_role_id = request.form.get("job_role_id")
        title = request.form.get("title", "").strip()
        drive_date = request.form.get("drive_date")
        application_deadline = request.form.get("application_deadline")
        selection_process = request.form.get("selection_process", "").strip()
        status = request.form.get("status", "Upcoming")

        success, msg = PlacementService.update_drive(
            drive_id=drive_id,
            company_id=int(company_id),
            job_role_id=int(job_role_id),
            title=title,
            drive_date=drive_date,
            application_deadline=application_deadline,
            selection_process=selection_process,
            status=status
        )

        if success:
            flash(msg, "success")
            return redirect(url_for("placements.list_drives"))
        else:
            flash(msg, "danger")

    return render_template("placements/drive_form.html", companies=companies, drive=drive)

@placement_bp.route("/drives/<int:drive_id>/delete", methods=["POST"])
@admin_required
def delete_drive(drive_id):
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Session token expired.", "danger")
        return redirect(url_for("placements.list_drives"))

    success, msg = PlacementService.delete_drive(drive_id)
    flash(msg, "success" if success else "danger")
    return redirect(url_for("placements.list_drives"))

@placement_bp.route("/drives/<int:drive_id>/apply", methods=["POST"])
@student_required
def apply_drive(drive_id):
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Session token expired.", "danger")
        return redirect(url_for("placements.list_drives"))

    student_id = session.get("student_id")
    if not student_id:
        student = StudentService.get_student_by_user_id(session["user_id"])
        if not student:
            flash("Student profile not found.", "danger")
            return redirect(url_for("dashboard.dashboard"))
        student_id = student.id
        session["student_id"] = student.id

    notes = request.form.get("notes")
    success, msg = PlacementService.apply_for_drive(drive_id, student_id, notes)
    if success:
        flash("Application submitted successfully!", "success")
    else:
        flash(f"Application rejected: {msg}", "danger")

    return redirect(url_for("placements.applications"))

@placement_bp.route("/applications")
@login_required
def applications():
    role = session.get("role")
    if role == "admin":
        drive_id = request.args.get("drive_id")
        if drive_id:
            apps = PlacementService.get_drive_applications(int(drive_id))
        else:
            from database.db import query_db
            apps = query_db("""
                SELECT a.*, u.full_name as student_name, u.email as student_email,
                       s.student_id_number, s.department,
                       ac.cgpa as student_cgpa, ac.backlogs as student_backlogs,
                       c.name as company_name, j.role_name, d.title as drive_title
                FROM applications a
                JOIN students s ON a.student_id = s.id
                JOIN users u ON s.user_id = u.id
                LEFT JOIN academic_details ac ON s.id = ac.student_id
                JOIN placement_drives d ON a.drive_id = d.id
                JOIN companies c ON d.company_id = c.id
                JOIN job_roles j ON d.job_role_id = j.id
                ORDER BY a.applied_at DESC
            """)
            apps = [dict(r) for r in apps]
        drives = PlacementService.get_all_drives()
        return render_template("placements/applications.html", applications=apps, drives=drives, selected_drive_id=drive_id)

    elif role == "student":
        student_id = session.get("student_id")
        apps = PlacementService.get_student_applications(student_id)
        return render_template("placements/applications.html", applications=apps)

@placement_bp.route("/applications/<int:app_id>/status", methods=["POST"])
@admin_required
def update_application_status(app_id):
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Session token expired.", "danger")
        return redirect(url_for("placements.applications"))

    new_status = request.form.get("status")
    notes = request.form.get("notes")
    success, msg = PlacementService.update_application_status(app_id, new_status, notes)
    if success:
        flash(f"Application status updated to '{new_status}'.", "success")
    else:
        flash(msg, "danger")

    return redirect(url_for("placements.applications"))

@placement_bp.route("/placement-history")
@login_required
def placement_history():
    from database.db import query_db
    records = query_db("""
        SELECT a.id, a.applied_at, a.notes,
               u.full_name as student_name, s.student_id_number, s.department, s.graduation_year,
               c.name as company_name, j.role_name, j.salary_package,
               d.title as drive_title, d.drive_date
        FROM applications a
        JOIN students s ON a.student_id = s.id
        JOIN users u ON s.user_id = u.id
        JOIN placement_drives d ON a.drive_id = d.id
        JOIN companies c ON d.company_id = c.id
        JOIN job_roles j ON d.job_role_id = j.id
        WHERE a.status = 'Selected'
        ORDER BY d.drive_date DESC, u.full_name ASC
    """)
    return render_template("placements/placement_history.html", placed_records=[dict(r) for r in records])
