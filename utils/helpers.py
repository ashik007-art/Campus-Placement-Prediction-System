"""Session authentication decorators, CSRF helpers, and presentation helpers."""
import secrets
from functools import wraps
from flask import session, redirect, url_for, flash, request, abort, jsonify, g
from database.db import query_db

def generate_csrf_token():
    """Generate or retrieve a CSRF token for the session."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(24)
    return session["_csrf_token"]

def verify_csrf_token(token):
    """Verify submitted CSRF token against session token."""
    stored = session.get("_csrf_token")
    if not stored or not token:
        return False
    return secrets.compare_digest(stored, token)

def get_current_user():
    """Retrieve current logged in user from session and database."""
    if "user_id" not in session:
        return None
    if not hasattr(g, "current_user") or g.current_user is None:
        user = query_db("SELECT id, full_name, email, role FROM users WHERE id = ?", (session["user_id"],), one=True)
        g.current_user = dict(user) if user else None
    return g.current_user

def get_current_student():
    """Retrieve current student record if the logged in user is a student."""
    user = get_current_user()
    if not user or user.get("role") != "student":
        return None
    if not hasattr(g, "current_student") or g.current_student is None:
        st = query_db("SELECT * FROM students WHERE user_id = ?", (user["id"],), one=True)
        g.current_student = dict(st) if st else None
    return g.current_student

def login_required(f):
    """Decorator ensuring user is authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator ensuring authenticated user is an administrator."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in with administrator credentials.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        if session.get("role") != "admin":
            flash("Access denied: Administrator privileges required.", "danger")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """Decorator ensuring authenticated user is a student."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to view your student portal.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        if session.get("role") != "student":
            flash("Access restricted to student accounts.", "danger")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return decorated_function
