"""Placement drives and student applications management service."""
from datetime import date
from database.db import get_db, query_db, execute_db
from models.placement_drive import PlacementDrive, Application

class PlacementService:

    @staticmethod
    def get_all_drives(status=None, company_id=None):
        query = """
            SELECT d.*, c.name as company_name, c.location as company_location,
                   j.role_name, j.min_cgpa, j.max_backlogs, j.salary_package,
                   COUNT(a.id) as total_applications
            FROM placement_drives d
            JOIN companies c ON d.company_id = c.id
            JOIN job_roles j ON d.job_role_id = j.id
            LEFT JOIN applications a ON d.id = a.drive_id
            WHERE 1=1
        """
        params = []
        if status:
            query += " AND d.status = ?"
            params.append(status)
        if company_id:
            query += " AND d.company_id = ?"
            params.append(company_id)

        query += " GROUP BY d.id ORDER BY d.drive_date ASC"

        rows = query_db(query, params)
        drives = []
        for r in rows:
            drive = PlacementDrive(dict(r))
            drive.required_skills = PlacementService.get_drive_required_skills(drive.id)
            drives.append(drive)
        return drives

    @staticmethod
    def get_drive_by_id(drive_id):
        query = """
            SELECT d.*, c.name as company_name, c.location as company_location,
                   j.role_name, j.min_cgpa, j.max_backlogs, j.salary_package,
                   COUNT(a.id) as total_applications
            FROM placement_drives d
            JOIN companies c ON d.company_id = c.id
            JOIN job_roles j ON d.job_role_id = j.id
            LEFT JOIN applications a ON d.id = a.drive_id
            WHERE d.id = ?
            GROUP BY d.id
        """
        row = query_db(query, (drive_id,), one=True)
        if not row:
            return None
        drive = PlacementDrive(dict(row))
        drive.required_skills = PlacementService.get_drive_required_skills(drive.id)
        return drive

    @staticmethod
    def get_drive_required_skills(drive_id):
        query = """
            SELECT s.id, s.name, s.category, jrs.is_mandatory
            FROM placement_drives d
            JOIN job_required_skills jrs ON d.job_role_id = jrs.job_role_id
            JOIN skills s ON jrs.skill_id = s.id
            WHERE d.id = ?
            ORDER BY s.name ASC
        """
        return [dict(r) for r in query_db(query, (drive_id,))]

    @staticmethod
    def create_drive(company_id, job_role_id, title, drive_date, application_deadline, selection_process="", status="Upcoming"):
        try:
            did = execute_db("""
                INSERT INTO placement_drives (company_id, job_role_id, title, drive_date, application_deadline, selection_process, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, job_role_id, title.strip(), str(drive_date), str(application_deadline), selection_process.strip(), status))
            return True, did
        except Exception as e:
            return False, f"Failed to create drive: {str(e)}"

    @staticmethod
    def update_drive(drive_id, company_id, job_role_id, title, drive_date, application_deadline, selection_process, status):
        try:
            execute_db("""
                UPDATE placement_drives
                SET company_id = ?, job_role_id = ?, title = ?, drive_date = ?, application_deadline = ?, selection_process = ?, status = ?
                WHERE id = ?
            """, (company_id, job_role_id, title.strip(), str(drive_date), str(application_deadline), selection_process.strip(), status, drive_id))
            return True, "Drive updated successfully."
        except Exception as e:
            return False, f"Failed to update drive: {str(e)}"

    @staticmethod
    def delete_drive(drive_id):
        try:
            execute_db("DELETE FROM placement_drives WHERE id = ?", (drive_id,))
            return True, "Drive deleted successfully."
        except Exception as e:
            return False, f"Failed to delete drive: {str(e)}"

    # --- Student Applications ---
    @staticmethod
    def apply_for_drive(drive_id, student_id, notes=None):
        """Validate eligibility, deadline, and duplicates before registering application."""
        # Check drive existence
        drive = PlacementService.get_drive_by_id(drive_id)
        if not drive:
            return False, "Placement drive not found."

        # Check drive status
        if drive.status in ("Completed", "Cancelled"):
            return False, f"Cannot apply: Drive status is {drive.status}."

        # Check deadline
        today_str = date.today().isoformat()
        if drive.application_deadline and drive.application_deadline < today_str:
            return False, f"Application deadline ({drive.application_deadline}) has passed."

        # Check duplicate application
        existing = query_db("SELECT id FROM applications WHERE drive_id = ? AND student_id = ?", (drive_id, student_id), one=True)
        if existing:
            return False, "You have already applied for this placement drive."

        # Check eligibility criteria against student academics
        acad = query_db("SELECT cgpa, backlogs FROM academic_details WHERE student_id = ?", (student_id,), one=True)
        if not acad:
            return False, "Please complete your academic profile before applying."

        eligible, reason = drive.is_student_eligible(float(acad["cgpa"] or 0), int(acad["backlogs"] or 0))
        if not eligible:
            return False, f"Eligibility check failed: {reason}"

        # Register application
        try:
            aid = execute_db("""
                INSERT INTO applications (drive_id, student_id, status, notes)
                VALUES (?, ?, 'Applied', ?)
            """, (drive_id, student_id, notes))
            return True, aid
        except Exception as e:
            return False, f"Failed to submit application: {str(e)}"

    @staticmethod
    def get_student_applications(student_id):
        query = """
            SELECT a.*, d.title as drive_title, d.drive_date, d.status as drive_status,
                   c.name as company_name, j.role_name, j.salary_package
            FROM applications a
            JOIN placement_drives d ON a.drive_id = d.id
            JOIN companies c ON d.company_id = c.id
            JOIN job_roles j ON d.job_role_id = j.id
            WHERE a.student_id = ?
            ORDER BY a.applied_at DESC
        """
        rows = query_db(query, (student_id,))
        return [Application(dict(r)) for r in rows]

    @staticmethod
    def get_drive_applications(drive_id):
        query = """
            SELECT a.*, u.full_name as student_name, u.email as student_email,
                   s.student_id_number, s.department, s.graduation_year,
                   ac.cgpa as student_cgpa, ac.backlogs as student_backlogs
            FROM applications a
            JOIN students s ON a.student_id = s.id
            JOIN users u ON s.user_id = u.id
            LEFT JOIN academic_details ac ON s.id = ac.student_id
            WHERE a.drive_id = ?
            ORDER BY ac.cgpa DESC, a.applied_at ASC
        """
        return [dict(r) for r in query_db(query, (drive_id,))]

    @staticmethod
    def update_application_status(application_id, status, notes=None):
        try:
            valid_statuses = ("Applied", "Shortlisted", "Interview", "Selected", "Rejected")
            if status not in valid_statuses:
                return False, f"Invalid status: {status}"

            if notes:
                execute_db("UPDATE applications SET status = ?, notes = ? WHERE id = ?", (status, notes.strip(), application_id))
            else:
                execute_db("UPDATE applications SET status = ? WHERE id = ?", (status, application_id))
            return True, "Application status updated successfully."
        except Exception as e:
            return False, f"Failed to update status: {str(e)}"

    @staticmethod
    def get_application_by_id(application_id):
        query = """
            SELECT a.*, u.full_name as student_name, u.email as student_email,
                   c.name as company_name, j.role_name, d.title as drive_title
            FROM applications a
            JOIN students s ON a.student_id = s.id
            JOIN users u ON s.user_id = u.id
            JOIN placement_drives d ON a.drive_id = d.id
            JOIN companies c ON d.company_id = c.id
            JOIN job_roles j ON d.job_role_id = j.id
            WHERE a.id = ?
        """
        row = query_db(query, (application_id,), one=True)
        return Application(dict(row)) if row else None
