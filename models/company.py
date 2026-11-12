"""Company and JobRole domain models."""

class Company:
    """Represents a recruiting organization."""

    def __init__(self, data=None):
        data = data or {}
        self.id = data.get("id")
        self.name = data.get("name", "")
        self.industry = data.get("industry", "")
        self.description = data.get("description", "")
        self.website = data.get("website", "")
        self.location = data.get("location", "")
        self.created_at = data.get("created_at")
        self.job_roles = data.get("job_roles", [])

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "industry": self.industry,
            "description": self.description,
            "website": self.website,
            "location": self.location,
            "job_roles": [r.to_dict() if hasattr(r, "to_dict") else r for r in self.job_roles]
        }

class JobRole:
    """Represents a specific vacancy or role offered by a company."""

    def __init__(self, data=None):
        data = data or {}
        self.id = data.get("id")
        self.company_id = data.get("company_id")
        self.company_name = data.get("company_name", "")
        self.role_name = data.get("role_name", "")
        self.min_cgpa = float(data.get("min_cgpa", 6.0))
        self.max_backlogs = int(data.get("max_backlogs", 0))
        self.salary_package = data.get("salary_package", "")
        self.description = data.get("description", "")
        self.required_skills = data.get("required_skills", [])

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "role_name": self.role_name,
            "min_cgpa": self.min_cgpa,
            "max_backlogs": self.max_backlogs,
            "salary_package": self.salary_package,
            "description": self.description,
            "required_skills": self.required_skills
        }
