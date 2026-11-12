"""Institutional reports, placement statistics, and CSV export routes."""
import csv
import io
from flask import Blueprint, render_template, request, Response, session
from utils.helpers import admin_required
from services.report_service import ReportService
from services.student_service import StudentService
from services.prediction_service import PredictionService

report_bp = Blueprint("reports", __name__)

@report_bp.route("/reports")
@admin_required
def reports():
    year = request.args.get("graduation_year")
    dept_reports = ReportService.get_department_report(graduation_year=year)
    company_reports = ReportService.get_company_report()
    drive_reports = ReportService.get_drive_summary_report()
    prediction_reports = PredictionService.get_all_predictions(limit=50)
    years = StudentService.get_distinct_graduation_years()

    return render_template(
        "reports/reports.html",
        dept_reports=dept_reports,
        company_reports=company_reports,
        drive_reports=drive_reports,
        prediction_reports=prediction_reports,
        years=years,
        selected_year=year
    )

@report_bp.route("/reports/export-csv")
@admin_required
def export_csv():
    report_type = request.args.get("type", "departments")
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == "departments":
        writer.writerow(["Department", "Total Students", "Average CGPA", "Selected Students", "Total Applications"])
        rows = ReportService.get_department_report()
        for r in rows:
            writer.writerow([r["department"], r["student_count"], r["avg_cgpa"], r["selected_students"], r["total_applications"]])
        filename = "department_placement_report.csv"

    elif report_type == "companies":
        writer.writerow(["Company Name", "Industry", "Location", "Total Drives", "Applications Received", "Hires Made"])
        rows = ReportService.get_company_report()
        for r in rows:
            writer.writerow([r["name"], r["industry"], r["location"], r["total_drives"], r["applications_received"], r["hires_made"]])
        filename = "company_hiring_report.csv"

    elif report_type == "drives":
        writer.writerow(["Drive Title", "Drive Date", "Status", "Company", "Job Role", "Package", "Total Applicants", "Shortlisted", "Selected"])
        rows = ReportService.get_drive_summary_report()
        for r in rows:
            writer.writerow([r["title"], r["drive_date"], r["status"], r["company_name"], r["role_name"], r["salary_package"], r["total_applicants"], r["shortlisted"], r["selected"]])
        filename = "placement_drive_summary_report.csv"

    else:
        writer.writerow(["ID", "Student", "Mode", "Readiness Score", "Category", "Key Factors", "Timestamp"])
        rows = PredictionService.get_all_predictions(limit=500)
        for r in rows:
            writer.writerow([r["id"], r["student_name"], r["mode"], r["readiness_score"], r["readiness_category"], r["key_factors"], r["created_at"]])
        filename = "prediction_history_report.csv"

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
