"""Recommendation record domain model."""

class RecommendationRecord:
    """Represents a rule-driven personalized recommendation."""

    def __init__(self, data=None):
        data = data or {}
        self.id = data.get("id")
        self.student_id = data.get("student_id")
        self.category = data.get("category", "General")
        self.title = data.get("title", "")
        self.description = data.get("description", "")
        self.priority = data.get("priority", "Medium")
        self.created_at = data.get("created_at")

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "created_at": self.created_at
        }
