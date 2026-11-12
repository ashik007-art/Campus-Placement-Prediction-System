"""Authentication and Session Management Routes."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database.db import query_db
from utils.helpers import verify_csrf_token
from utils.validators import validate_email_format, validate_password_strength
from services.student_service import StudentService

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        csrf_token = request.form.get("csrf_token")
        if not verify_csrf_token(csrf_token):
            flash("Invalid or expired session security token. Please try again.", "danger")
            return render_template("login.html")

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email address and password.", "warning")
            return render_template("login.html")

        user = query_db("SELECT * FROM users WHERE email = ?", (email,), one=True)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email address or password. Please verify your credentials.", "danger")
            return render_template("login.html")

        # Session setup
        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["full_name"]
        session["email"] = user["email"]
        session["role"] = user["role"]

        if user["role"] == "student":
            st = query_db("SELECT id FROM students WHERE user_id = ?", (user["id"],), one=True)
            if st:
                session["student_id"] = st["id"]

        flash(f"Welcome back, {user['full_name']}!", "success")
        next_url = request.args.get("next")
        if next_url and next_url.startswith("/"):
            return redirect(next_url)
        return redirect(url_for("dashboard.dashboard"))

    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        csrf_token = request.form.get("csrf_token")
        if not verify_csrf_token(csrf_token):
            flash("Security verification failed. Please try again.", "danger")
            return render_template("register.html")

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        student_id_number = request.form.get("student_id_number", "").strip().upper()
        department = request.form.get("department", "").strip()
        graduation_year = request.form.get("graduation_year", "")
        phone = request.form.get("phone", "").strip()

        # Validations
        if not all([full_name, email, password, student_id_number, department, graduation_year]):
            flash("All required fields must be completed.", "warning")
            return render_template("register.html")

        if not validate_email_format(email):
            flash("Please provide a valid email address.", "warning")
            return render_template("register.html")

        is_valid_pwd, pwd_msg = validate_password_strength(password)
        if not is_valid_pwd:
            flash(pwd_msg, "warning")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "warning")
            return render_template("register.html")

        success, result = StudentService.create_student(
            full_name=full_name,
            email=email,
            password=password,
            student_id_number=student_id_number,
            department=department,
            graduation_year=graduation_year,
            phone=phone
        )

        if not success:
            flash(result, "danger")
            return render_template("register.html")

        flash("Registration successful! You can now log in with your credentials.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("auth.login"))
