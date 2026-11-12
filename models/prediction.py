"""Prediction result model."""

class PredictionRecord:
    """Represents a placement readiness prediction assessment."""

    def __init__(self, data=None):
        data = data or {}
        self.id = data.get("id")
        self.student_id = data.get("student_id")
        self.student_name = data.get("student_name", "")
        self.mode = data.get("mode", "Demo Readiness Score")
        self.readiness_score = float(data.get("readiness_score", 0.0))
        self.readiness_category = data.get("readiness_category", "Needs Improvement")
        self.key_factors = data.get("key_factors", "")
        self.created_at = data.get("created_at")

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": self.student_name,
            "mode": self.mode,
            "readiness_score": self.readiness_score,
            "readiness_category": self.readiness_category,
            "key_factors": self.key_factors,
            "created_at": self.created_at
        }
