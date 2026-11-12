"""Placement drive and student application models."""

class PlacementDrive:
    """Represents an active or upcoming campus recruitment drive."""

    def __init__(self, data=None):
        data = data or {}
        self.id = data.get("id")
        self.company_id = data.get("company_id")
        self.company_name = data.get("company_name", "")
        self.company_location = data.get("company_location", "")
        self.job_role_id = data.get("job_role_id")
        self.role_name = data.get("role_name", "")
        self.min_cgpa = float(data.get("min_cgpa", 6.0))
        self.max_backlogs = int(data.get("max_backlogs", 0))
        self.salary_package = data.get("salary_package", "")
        self.title = data.get("title", "")
        self.drive_date = data.get("drive_date", "")
        self.application_deadline = data.get("application_deadline", "")
        self.selection_process = data.get("selection_process", "")
        self.status = data.get("status", "Upcoming")
        self.required_skills = data.get("required_skills", [])
        self.total_applications = data.get("total_applications", 0)

    def is_student_eligible(self, student_cgpa: float, student_backlogs: int) -> tuple[bool, str]:
        """Check if a student meets basic eligibility thresholds."""
        if student_cgpa < self.min_cgpa:
            return False, f"CGPA {student_cgpa:.2f} is below minimum requirement of {self.min_cgpa:.2f}"
        if student_backlogs > self.max_backlogs:
            return False, f"Backlogs ({student_backlogs}) exceed maximum allowed ({self.max_backlogs})"
        return True, "Eligible"

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "job_role_id": self.job_role_id,
            "role_name": self.role_name,
            "title": self.title,
            "drive_date": self.drive_date,
            "application_deadline": self.application_deadline,
            "selection_process": self.selection_process,
            "status": self.status,
            "min_cgpa": self.min_cgpa,
            "max_backlogs": self.max_backlogs,
            "salary_package": self.salary_package,
            "required_skills": self.required_skills,
            "total_applications": self.total_applications
        }

class Application:
    """Represents a student's application to a placement drive."""

    def __init__(self, data=None):
        data = data or {}
        self.id = data.get("id")
        self.drive_id = data.get("drive_id")
        self.student_id = data.get("student_id")
        self.student_name = data.get("student_name", "")
        self.student_email = data.get("student_email", "")
        self.student_cgpa = data.get("student_cgpa", 0.0)
        self.company_name = data.get("company_name", "")
        self.role_name = data.get("role_name", "")
        self.drive_title = data.get("drive_title", "")
        self.status = data.get("status", "Applied")
        self.applied_at = data.get("applied_at", "")
        self.notes = data.get("notes", "")

    def to_dict(self):
        return {
            "id": self.id,
            "drive_id": self.drive_id,
            "student_id": self.student_id,
            "student_name": self.student_name,
            "company_name": self.company_name,
            "role_name": self.role_name,
            "status": self.status,
            "applied_at": self.applied_at,
            "notes": self.notes
        }
