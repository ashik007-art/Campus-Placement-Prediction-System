"""Main entry point for Campus Placement Prediction System."""
import os
import sys
from pathlib import Path
from flask import Flask, render_template

# Add root directory to path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import Config
from database.db import close_db, init_db, query_db
from database.seed import seed_database
from utils.helpers import get_current_user, get_current_student, generate_csrf_token

def create_app(config_class=Config):
    """Application factory for Campus Placement Prediction System."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Teardown database connection
    app.teardown_appcontext(close_db)

    # Global context processors available in all templates
    @app.context_processor
    def inject_globals():
        return {
            "current_user": get_current_user(),
            "current_student": get_current_student(),
            "csrf_token": generate_csrf_token()
        }

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/404.html", message="403 Forbidden - Access Denied"), 403

    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.student_routes import student_bp
    from routes.company_routes import company_bp
    from routes.placement_routes import placement_bp
    from routes.prediction_routes import prediction_bp
    from routes.recommendation_routes import recommendation_bp
    from routes.report_routes import report_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(placement_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(report_bp)

    # First-run automated database initialization
    with app.app_context():
        try:
            # Check if users table exists
            check = query_db("SELECT name FROM sqlite_master WHERE type='table' AND name='users'", one=True)
            if not check:
                print("[*] Initializing database schema on first launch...")
                init_db()
                if not app.config.get("TESTING"):
                    print("[*] Seeding default demonstration records...")
                    seed_database(app.config.get("DATABASE_PATH"))
        except Exception as e:
            print(f"[Warning] First-run database initialization notice: {e}")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
