from .auth_routes import auth_bp
from .dashboard_routes import dashboard_bp
from .student_routes import student_bp
from .company_routes import company_bp
from .placement_routes import placement_bp
from .prediction_routes import prediction_bp
from .recommendation_routes import recommendation_bp
from .report_routes import report_bp

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "student_routes",
    "company_bp",
    "placement_bp",
    "prediction_bp",
    "recommendation_bp",
    "report_bp"
]
