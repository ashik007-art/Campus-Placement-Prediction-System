"""Analytics, reporting, and dashboard aggregation service."""
from database.db import query_db

class ReportService:

    @staticmethod
    def get_admin_dashboard_metrics():
        """Retrieve real aggregated metrics for the administrator dashboard."""
        total_students = query_db("SELECT COUNT(*) as cnt FROM students", one=True)["cnt"]
        total_companies = query_db("SELECT COUNT(*) as cnt FROM companies", one=True)["cnt"]
        total_drives = query_db("SELECT COUNT(*) as cnt FROM placement_drives", one=True)["cnt"]
        total_applications = query_db("SELECT COUNT(*) as cnt FROM applications", one=True)["cnt"]
        selected_students = query_db("SELECT COUNT(DISTINCT student_id) as cnt FROM applications WHERE status = 'Selected'", one=True)["cnt"]

        # Department-wise counts and selections
        dept_stats = query_db("""
            SELECT s.department,
                   COUNT(DISTINCT s.id) as total_students,
                   COUNT(DISTINCT CASE WHEN a.status = 'Selected' THEN s.id END) as selected_count
            FROM students s
            LEFT JOIN applications a ON s.id = a.student_id
            WHERE s.department IS NOT NULL AND s.department != ''
            GROUP BY s.department
            ORDER BY total_students DESC
        """)

        # Application status breakdown
        status_stats = query_db("""
            SELECT status, COUNT(*) as count
            FROM applications
            GROUP BY status
        """)

        # Upcoming drives
        upcoming_drives = query_db("""
            SELECT d.id, d.title, d.drive_date, d.status, c.name as company_name, j.role_name, j.salary_package
            FROM placement_drives d
            JOIN companies c ON d.company_id = c.id
            JOIN job_roles j ON d.job_role_id = j.id
            WHERE d.status IN ('Upcoming', 'Ongoing')
            ORDER BY d.drive_date ASC
            LIMIT 5
        """)

        # Recent registrations
        recent_students = query_db("""
            SELECT s.id, s.student_id_number, s.department, s.graduation_year, u.full_name, u.email, u.created_at, ac.cgpa
            FROM students s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN academic_details ac ON s.id = ac.student_id
            ORDER BY u.created_at DESC
            LIMIT 5
        """)

        # Prediction categories breakdown
        pred_stats = query_db("""
            SELECT readiness_category, COUNT(*) as count
            FROM predictions
            GROUP BY readiness_category
        """)

        return {
            "total_students": total_students,
            "total_companies": total_companies,
            "total_drives": total_drives,
            "total_applications": total_applications,
            "selected_students": selected_students,
            "placement_rate": round((selected_students / total_students * 100), 1) if total_students > 0 else 0.0,
            "department_stats": [dict(r) for r in dept_stats],
            "application_status_stats": [dict(r) for r in status_stats],
            "upcoming_drives": [dict(r) for r in upcoming_drives],
            "recent_students": [dict(r) for r in recent_students],
            "prediction_stats": [dict(r) for r in pred_stats]
        }

    @staticmethod
    def get_department_report(graduation_year=None):
        query = """
            SELECT s.department,
                   COUNT(DISTINCT s.id) as student_count,
                   ROUND(AVG(ac.cgpa), 2) as avg_cgpa,
                   COUNT(DISTINCT CASE WHEN a.status = 'Selected' THEN s.id END) as selected_students,
                   COUNT(a.id) as total_applications
            FROM students s
            LEFT JOIN academic_details ac ON s.id = ac.student_id
            LEFT JOIN applications a ON s.id = a.student_id
            WHERE 1=1
        """
        params = []
        if graduation_year:
            query += " AND s.graduation_year = ?"
            params.append(graduation_year)
        query += " GROUP BY s.department ORDER BY student_count DESC"
        return [dict(r) for r in query_db(query, params)]

    @staticmethod
    def get_company_report():
        query = """
            SELECT c.name, c.industry, c.location,
                   COUNT(DISTINCT d.id) as total_drives,
                   COUNT(a.id) as applications_received,
                   COUNT(CASE WHEN a.status = 'Selected' THEN 1 END) as hires_made
            FROM companies c
            LEFT JOIN placement_drives d ON c.id = d.company_id
            LEFT JOIN applications a ON d.id = a.drive_id
            GROUP BY c.id
            ORDER BY hires_made DESC, applications_received DESC
        """
        return [dict(r) for r in query_db(query)]

    @staticmethod
    def get_drive_summary_report():
        query = """
            SELECT d.title, d.drive_date, d.status,
                   c.name as company_name, j.role_name, j.salary_package,
                   COUNT(a.id) as total_applicants,
                   COUNT(CASE WHEN a.status = 'Shortlisted' THEN 1 END) as shortlisted,
                   COUNT(CASE WHEN a.status = 'Selected' THEN 1 END) as selected
            FROM placement_drives d
            JOIN companies c ON d.company_id = c.id
            JOIN job_roles j ON d.job_role_id = j.id
            LEFT JOIN applications a ON d.id = a.drive_id
            GROUP BY d.id
            ORDER BY d.drive_date DESC
        """
        return [dict(r) for r in query_db(query)]
