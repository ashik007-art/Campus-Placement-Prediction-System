"""Student domain model and profile representation."""

class Student:
    """Represents a student profile, academic metrics, and credentials."""

    def __init__(self, data=None):
        data = data or {}
        self.id = data.get("id")
        self.user_id = data.get("user_id")
        self.student_id_number = data.get("student_id_number", "")
        self.full_name = data.get("full_name", "")
        self.email = data.get("email", "")
        self.phone = data.get("phone", "")
        self.department = data.get("department", "")
        self.graduation_year = data.get("graduation_year", "")
        self.communication_level = data.get("communication_level", "Intermediate")
        self.aptitude_level = data.get("aptitude_level", "Intermediate")
        self.resume_url = data.get("resume_url", "")
        self.created_at = data.get("created_at")

        # Academic Details
        self.tenth_percentage = data.get("tenth_percentage", 0.0)
        self.twelfth_percentage = data.get("twelfth_percentage", 0.0)
        self.cgpa = data.get("cgpa", 0.0)
        self.backlogs = data.get("backlogs", 0)
        self.attendance_percentage = data.get("attendance_percentage", 85.0)

        # Related collections
        self.skills = data.get("skills", [])
        self.certifications = data.get("certifications", [])
        self.internships = data.get("internships", [])
        self.projects = data.get("projects", [])

    @property
    def profile_completion(self) -> int:
        """Calculate overall profile completion percentage."""
        score = 0
        total_items = 8

        if self.student_id_number and self.department and self.graduation_year:
            score += 1
        if self.tenth_percentage and self.twelfth_percentage:
            score += 1
        if self.cgpa:
            score += 1
        if self.attendance_percentage:
            score += 1
        if self.skills and len(self.skills) > 0:
            score += 1
        if self.projects and len(self.projects) > 0:
            score += 1
        if self.internships and len(self.internships) > 0:
            score += 1
        if self.certifications and len(self.certifications) > 0:
            score += 1

        return int((score / total_items) * 100)

    @property
    def has_backlogs(self) -> bool:
        return (self.backlogs or 0) > 0

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "student_id_number": self.student_id_number,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "department": self.department,
            "graduation_year": self.graduation_year,
            "communication_level": self.communication_level,
            "aptitude_level": self.aptitude_level,
            "tenth_percentage": self.tenth_percentage,
            "twelfth_percentage": self.twelfth_percentage,
            "cgpa": self.cgpa,
            "backlogs": self.backlogs,
            "attendance_percentage": self.attendance_percentage,
            "profile_completion": self.profile_completion
        }
