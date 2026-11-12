"""Student profile, academic records, skills, and portfolio routes."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from utils.helpers import login_required, admin_required, verify_csrf_token
from utils.validators import validate_percentage, validate_cgpa, validate_non_negative_int, validate_email_format
from services.student_service import StudentService
from services.prediction_service import PredictionService
from services.recommendation_service import RecommendationService

student_bp = Blueprint("students", __name__)

def check_student_access(student_id):
    """Enforce authorization: Admin or the student themselves."""
    role = session.get("role")
    if role == "admin":
        return True
    if role == "student" and session.get("student_id") == student_id:
        return True
    return False

@student_bp.route("/students")
@admin_required
def list_students():
    dept = request.args.get("department")
    year = request.args.get("graduation_year")
    search = request.args.get("search")

    students = StudentService.get_all_students(department=dept, graduation_year=year, search=search)
    departments = StudentService.get_distinct_departments()
    years = StudentService.get_distinct_graduation_years()

    return render_template(
        "students/students.html",
        students=students,
        departments=departments,
        years=years,
        selected_dept=dept,
        selected_year=year,
        search=search
    )

@student_bp.route("/students/add", methods=["GET", "POST"])
@admin_required
def add_student():
    if request.method == "POST":
        if not verify_csrf_token(request.form.get("csrf_token")):
            flash("Session security token expired.", "danger")
            return redirect(url_for("students.add_student"))

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        student_id_number = request.form.get("student_id_number", "").strip().upper()
        department = request.form.get("department", "").strip()
        graduation_year = request.form.get("graduation_year")
        phone = request.form.get("phone", "").strip()
        tenth = request.form.get("tenth_percentage", 75.0)
        twelfth = request.form.get("twelfth_percentage", 75.0)
        cgpa = request.form.get("cgpa", 7.0)
        backlogs = request.form.get("backlogs", 0)
        attendance = request.form.get("attendance_percentage", 85.0)

        # Validation
        val_t, msg_t = validate_percentage(tenth)
        val_w, msg_w = validate_percentage(twelfth)
        val_c, msg_c = validate_cgpa(cgpa)
        val_b, msg_b = validate_non_negative_int(backlogs, "Backlogs")
        val_a, msg_a = validate_percentage(attendance)

        if not (val_t and val_w and val_c and val_b and val_a):
            flash(msg_t or msg_w or msg_c or msg_b or msg_a, "warning")
            return render_template("students/student_form.html")

        success, res = StudentService.create_student(
            full_name=full_name,
            email=email,
            password=password,
            student_id_number=student_id_number,
            department=department,
            graduation_year=graduation_year,
            phone=phone,
            tenth=tenth,
            twelfth=twelfth,
            cgpa=cgpa,
            backlogs=backlogs,
            attendance=attendance
        )
        if success:
            flash("Student created successfully.", "success")
            return redirect(url_for("students.view_student", student_id=res))
        else:
            flash(res, "danger")

    return render_template("students/student_form.html")

@student_bp.route("/students/<int:student_id>")
@login_required
def view_student(student_id):
    if not check_student_access(student_id):
        flash("Unauthorized access to student record.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    student = StudentService.get_student_by_id(student_id)
    if not student:
        flash("Student record not found.", "warning")
        return redirect(url_for("dashboard.dashboard"))

    all_master_skills = StudentService.get_all_master_skills()
    latest_prediction = PredictionService.get_latest_prediction(student_id)
    recommendations = RecommendationService.get_student_recommendations(student_id)

    return render_template(
        "students/student_detail.html",
        student=student,
        master_skills=all_master_skills,
        latest_prediction=latest_prediction,
        recommendations=recommendations
    )

@student_bp.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    if not check_student_access(student_id):
        flash("Unauthorized access.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    student = StudentService.get_student_by_id(student_id)
    if not student:
        flash("Student not found.", "warning")
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        if not verify_csrf_token(request.form.get("csrf_token")):
            flash("Security verification failed.", "danger")
            return redirect(url_for("students.edit_student", student_id=student_id))

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        department = request.form.get("department", "").strip()
        graduation_year = request.form.get("graduation_year")
        phone = request.form.get("phone", "").strip()
        comm_level = request.form.get("communication_level", "Intermediate")
        apt_level = request.form.get("aptitude_level", "Intermediate")
        resume_url = request.form.get("resume_url", "").strip()

        tenth = request.form.get("tenth_percentage")
        twelfth = request.form.get("twelfth_percentage")
        cgpa = request.form.get("cgpa")
        backlogs = request.form.get("backlogs")
        attendance = request.form.get("attendance_percentage")

        # Validate numbers
        val_t, msg_t = validate_percentage(tenth)
        val_w, msg_w = validate_percentage(twelfth)
        val_c, msg_c = validate_cgpa(cgpa)
        val_b, msg_b = validate_non_negative_int(backlogs, "Backlogs")
        val_a, msg_a = validate_percentage(attendance)

        if not (val_t and val_w and val_c and val_b and val_a):
            flash(msg_t or msg_w or msg_c or msg_b or msg_a, "warning")
            return render_template("students/edit_student.html", student=student)

        success, msg = StudentService.update_student(
            student_id=student_id,
            full_name=full_name,
            email=email,
            department=department,
            graduation_year=graduation_year,
            phone=phone,
            comm_level=comm_level,
            apt_level=apt_level,
            resume_url=resume_url,
            tenth=tenth,
            twelfth=twelfth,
            cgpa=cgpa,
            backlogs=backlogs,
            attendance=attendance
        )

        if success:
            flash(msg, "success")
            return redirect(url_for("students.view_student", student_id=student_id))
        else:
            flash(msg, "danger")

    return render_template("students/edit_student.html", student=student)

@student_bp.route("/students/<int:student_id>/delete", methods=["POST"])
@admin_required
def delete_student(student_id):
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Security token expired.", "danger")
        return redirect(url_for("students.list_students"))

    success, msg = StudentService.delete_student(student_id)
    flash(msg, "success" if success else "danger")
    return redirect(url_for("students.list_students"))

# --- Skills Management Routes ---
@student_bp.route("/students/<int:student_id>/skills/add", methods=["POST"])
@login_required
def add_skill(student_id):
    if not check_student_access(student_id):
        abort(403)
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Security token expired.", "danger")
        return redirect(url_for("students.view_student", student_id=student_id))

    skill_id = request.form.get("skill_id")
    proficiency = request.form.get("proficiency", "Intermediate")
    if skill_id:
        StudentService.add_student_skill(student_id, int(skill_id), proficiency)
        flash("Skill updated successfully.", "success")
    return redirect(url_for("students.view_student", student_id=student_id))

@student_bp.route("/students/<int:student_id>/skills/<int:skill_id>/delete", methods=["POST"])
@login_required
def delete_skill(student_id, skill_id):
    if not check_student_access(student_id):
        abort(403)
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Security token expired.", "danger")
        return redirect(url_for("students.view_student", student_id=student_id))

    StudentService.remove_student_skill(student_id, skill_id)
    flash("Skill removed.", "info")
    return redirect(url_for("students.view_student", student_id=student_id))

# --- Internships, Projects, Certifications Routes ---
@student_bp.route("/students/<int:student_id>/internships/add", methods=["POST"])
@login_required
def add_internship(student_id):
    if not check_student_access(student_id):
        abort(403)
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Security token expired.", "danger")
        return redirect(url_for("students.view_student", student_id=student_id))

    company = request.form.get("company_name")
    role = request.form.get("role")
    duration = request.form.get("duration_months", 1)
    desc = request.form.get("description")
    s_dt = request.form.get("start_date")
    e_dt = request.form.get("end_date")

    if company and role:
        StudentService.add_internship(student_id, company, role, duration, desc, s_dt, e_dt)
        flash("Internship experience recorded.", "success")
    return redirect(url_for("students.view_student", student_id=student_id))

@student_bp.route("/students/<int:student_id>/internships/<int:intern_id>/delete", methods=["POST"])
@login_required
def delete_internship(student_id, intern_id):
    if not check_student_access(student_id):
        abort(403)
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Security token expired.", "danger")
        return redirect(url_for("students.view_student", student_id=student_id))

    StudentService.delete_internship(intern_id, student_id)
    flash("Internship removed.", "info")
    return redirect(url_for("students.view_student", student_id=student_id))

@student_bp.route("/students/<int:student_id>/projects/add", methods=["POST"])
@login_required
def add_project(student_id):
    if not check_student_access(student_id):
        abort(403)
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Security token expired.", "danger")
        return redirect(url_for("students.view_student", student_id=student_id))

    title = request.form.get("title")
    tech = request.form.get("tech_stack")
    desc = request.form.get("description")
    gh = request.form.get("github_url")

    if title:
        StudentService.add_project(student_id, title, tech, desc, gh)
        flash("Project added to portfolio.", "success")
    return redirect(url_for("students.view_student", student_id=student_id))

@student_bp.route("/students/<int:student_id>/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(student_id, project_id):
    if not check_student_access(student_id):
        abort(403)
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Security token expired.", "danger")
        return redirect(url_for("students.view_student", student_id=student_id))

    StudentService.delete_project(project_id, student_id)
    flash("Project removed.", "info")
    return redirect(url_for("students.view_student", student_id=student_id))

@student_bp.route("/students/<int:student_id>/certifications/add", methods=["POST"])
@login_required
def add_certification(student_id):
    if not check_student_access(student_id):
        abort(403)
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Security token expired.", "danger")
        return redirect(url_for("students.view_student", student_id=student_id))

    title = request.form.get("title")
    org = request.form.get("issuing_organization")
    issue_date = request.form.get("issue_date")
    url = request.form.get("credential_url")

    if title and org:
        StudentService.add_certification(student_id, title, org, issue_date, url)
        flash("Certification added.", "success")
    return redirect(url_for("students.view_student", student_id=student_id))

@student_bp.route("/students/<int:student_id>/certifications/<int:cert_id>/delete", methods=["POST"])
@login_required
def delete_certification(student_id, cert_id):
    if not check_student_access(student_id):
        abort(403)
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Security token expired.", "danger")
        return redirect(url_for("students.view_student", student_id=student_id))

    StudentService.delete_certification(cert_id, student_id)
    flash("Certification removed.", "info")
    return redirect(url_for("students.view_student", student_id=student_id))
