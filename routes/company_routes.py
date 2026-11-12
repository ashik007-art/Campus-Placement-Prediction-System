"""Company and Job Role Management Routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.helpers import login_required, admin_required, verify_csrf_token
from utils.validators import validate_cgpa, validate_non_negative_int
from services.company_service import CompanyService
from services.student_service import StudentService

company_bp = Blueprint("companies", __name__)

@company_bp.route("/companies")
@login_required
def list_companies():
    industry = request.args.get("industry")
    search = request.args.get("search")

    companies = CompanyService.get_all_companies(search=search, industry=industry)
    industries = CompanyService.get_distinct_industries()

    return render_template(
        "companies/companies.html",
        companies=companies,
        industries=industries,
        selected_industry=industry,
        search=search
    )

@company_bp.route("/companies/add", methods=["GET", "POST"])
@admin_required
def add_company():
    if request.method == "POST":
        if not verify_csrf_token(request.form.get("csrf_token")):
            flash("Session token expired.", "danger")
            return redirect(url_for("companies.add_company"))

        name = request.form.get("name", "").strip()
        industry = request.form.get("industry", "").strip()
        description = request.form.get("description", "").strip()
        website = request.form.get("website", "").strip()
        location = request.form.get("location", "").strip()

        if not name or not industry:
            flash("Company name and industry are required.", "warning")
            return render_template("companies/company_form.html")

        success, res = CompanyService.create_company(name, industry, description, website, location)
        if success:
            flash("Company registered successfully.", "success")
            return redirect(url_for("companies.view_company", company_id=res))
        else:
            flash(res, "danger")

    return render_template("companies/company_form.html", company=None)

@company_bp.route("/companies/<int:company_id>")
@login_required
def view_company(company_id):
    company = CompanyService.get_company_by_id(company_id)
    if not company:
        flash("Company not found.", "warning")
        return redirect(url_for("companies.list_companies"))

    all_master_skills = StudentService.get_all_master_skills()
    return render_template("companies/company_detail.html", company=company, master_skills=all_master_skills)

@company_bp.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_company(company_id):
    company = CompanyService.get_company_by_id(company_id)
    if not company:
        flash("Company not found.", "warning")
        return redirect(url_for("companies.list_companies"))

    if request.method == "POST":
        if not verify_csrf_token(request.form.get("csrf_token")):
            flash("Session token expired.", "danger")
            return redirect(url_for("companies.edit_company", company_id=company_id))

        name = request.form.get("name", "").strip()
        industry = request.form.get("industry", "").strip()
        description = request.form.get("description", "").strip()
        website = request.form.get("website", "").strip()
        location = request.form.get("location", "").strip()

        if not name or not industry:
            flash("Company name and industry are required.", "warning")
            return render_template("companies/company_form.html", company=company)

        success, msg = CompanyService.update_company(company_id, name, industry, description, website, location)
        if success:
            flash(msg, "success")
            return redirect(url_for("companies.view_company", company_id=company_id))
        else:
            flash(msg, "danger")

    return render_template("companies/company_form.html", company=company)

@company_bp.route("/companies/<int:company_id>/delete", methods=["POST"])
@admin_required
def delete_company(company_id):
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Session token expired.", "danger")
        return redirect(url_for("companies.list_companies"))

    success, msg = CompanyService.delete_company(company_id)
    flash(msg, "success" if success else "danger")
    return redirect(url_for("companies.list_companies"))

# --- Job Roles ---
@company_bp.route("/companies/<int:company_id>/roles/add", methods=["POST"])
@admin_required
def add_job_role(company_id):
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Session token expired.", "danger")
        return redirect(url_for("companies.view_company", company_id=company_id))

    role_name = request.form.get("role_name", "").strip()
    min_cgpa = request.form.get("min_cgpa", 6.0)
    max_backlogs = request.form.get("max_backlogs", 0)
    salary_package = request.form.get("salary_package", "").strip()
    description = request.form.get("description", "").strip()
    skill_ids = request.form.getlist("skill_ids")

    val_c, msg_c = validate_cgpa(min_cgpa)
    val_b, msg_b = validate_non_negative_int(max_backlogs, "Max backlogs")

    if not (val_c and val_b) or not role_name or not salary_package:
        flash(msg_c or msg_b or "Role title and package are required.", "warning")
        return redirect(url_for("companies.view_company", company_id=company_id))

    success, res = CompanyService.create_job_role(
        company_id=company_id,
        role_name=role_name,
        min_cgpa=min_cgpa,
        max_backlogs=max_backlogs,
        salary_package=salary_package,
        description=description,
        required_skill_ids=skill_ids
    )

    if success:
        flash("Job role added successfully.", "success")
    else:
        flash(res, "danger")

    return redirect(url_for("companies.view_company", company_id=company_id))

@company_bp.route("/companies/<int:company_id>/roles/<int:role_id>/delete", methods=["POST"])
@admin_required
def delete_job_role(company_id, role_id):
    if not verify_csrf_token(request.form.get("csrf_token")):
        flash("Session token expired.", "danger")
        return redirect(url_for("companies.view_company", company_id=company_id))

    CompanyService.delete_job_role(role_id)
    flash("Job role removed.", "info")
    return redirect(url_for("companies.view_company", company_id=company_id))
