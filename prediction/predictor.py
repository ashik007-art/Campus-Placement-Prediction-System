"""Inference engine supporting both Trained Machine Learning models and transparent Demo Scoring."""
import os
from pathlib import Path
from flask import current_app
from prediction.preprocessing import extract_features_from_student, map_level_to_score
from prediction.model_utils import load_model

def get_category_from_score(score: float) -> str:
    """Classify readiness score into standard project tiers."""
    if score >= 75.0:
        return "High Readiness"
    elif score >= 55.0:
        return "Moderate Readiness"
    else:
        return "Needs Improvement"

def calculate_demo_readiness(student_data: dict) -> dict:
    """
    Transparent rule-based heuristic score used when no trained ML model is present.
    Clearly designated as a Demo Readiness Score, NOT an ML calibrated probability.
    """
    cgpa = float(student_data.get("cgpa") or 0.0)
    backlogs = int(student_data.get("backlogs") or 0)
    tenth = float(student_data.get("tenth_percentage") or 0.0)
    twelfth = float(student_data.get("twelfth_percentage") or 0.0)
    attendance = float(student_data.get("attendance_percentage") or 85.0)

    skills = student_data.get("skills") or []
    skill_count = len(skills) if isinstance(skills, list) else int(student_data.get("skill_count") or 0)

    projects = student_data.get("projects") or []
    project_count = len(projects) if isinstance(projects, list) else int(student_data.get("project_count") or 0)

    internships = student_data.get("internships") or []
    internship_count = len(internships) if isinstance(internships, list) else int(student_data.get("internship_count") or 0)

    comm_score = map_level_to_score(student_data.get("communication_level"))
    apt_score = map_level_to_score(student_data.get("aptitude_level"))

    # Scoring Components (Total 100 points maximum)
    # 1. CGPA Component (30 points)
    cgpa_pts = (min(cgpa, 10.0) / 10.0) * 30.0

    # 2. School / Intermediate Academics (15 points)
    academic_avg = (tenth + twelfth) / 2.0
    school_pts = (min(academic_avg, 100.0) / 100.0) * 15.0

    # 3. Practical Experience: Internships (15 points) & Projects (12 points)
    internship_pts = min(internship_count * 7.5, 15.0)
    project_pts = min(project_count * 4.0, 12.0)

    # 4. Technical Skills (14 points)
    skill_pts = min(skill_count * 2.8, 14.0)

    # 5. Aptitude and Communication (14 points: 7 each)
    comm_pts = (comm_score / 3.0) * 7.0
    apt_pts = (apt_score / 3.0) * 7.0

    gross_score = cgpa_pts + school_pts + internship_pts + project_pts + skill_pts + comm_pts + apt_pts

    # Penalties
    backlog_penalty = backlogs * 15.0
    attendance_penalty = 5.0 if attendance < 75.0 else 0.0

    final_score = max(0.0, min(100.0, gross_score - backlog_penalty - attendance_penalty))
    final_score = round(final_score, 1)

    factors = []
    if cgpa >= 8.0:
        factors.append(f"Excellent CGPA ({cgpa:.2f}) gives strong academic weight (+{cgpa_pts:.1f} pts)")
    elif cgpa < 6.5:
        factors.append(f"Low CGPA ({cgpa:.2f}) limits competitive advantage")

    if backlogs > 0:
        factors.append(f"Active backlogs count ({backlogs}) applied severe penalty (-{backlog_penalty:.1f} pts)")
    else:
        factors.append("Zero active backlogs satisfies initial company screening thresholds")

    if internship_count > 0:
        factors.append(f"Verified internship experience ({internship_count}) significantly boosts readiness (+{internship_pts:.1f} pts)")
    else:
        factors.append("No recorded internship experience; recommended to complete at least one")

    if skill_count >= 4:
        factors.append(f"Diverse technical skill stack ({skill_count} skills) enhances versatility (+{skill_pts:.1f} pts)")
    else:
        factors.append("Limited technical skill portfolio; expanding core proficiencies will improve readiness")

    category = get_category_from_score(final_score)

    return {
        "mode": "Demo Readiness Score",
        "readiness_score": final_score,
        "readiness_category": category,
        "key_factors": "; ".join(factors),
        "breakdown": {
            "academic_points": round(cgpa_pts + school_pts, 1),
            "experience_points": round(internship_pts + project_pts, 1),
            "skill_points": round(skill_pts, 1),
            "soft_skills_points": round(comm_pts + apt_pts, 1),
            "penalties": round(backlog_penalty + attendance_penalty, 1)
        },
        "disclaimer": "This readiness assessment is generated via transparent rule-based demo heuristics. It provides directional academic feedback and does not guarantee job selection or employment."
    }

def predict_placement(student_data: dict, model_path: str = None, preprocessor_path: str = None) -> dict:
    """
    Main prediction entry point.
    If a trained Scikit-learn model and preprocessor exist, runs machine learning inference.
    Otherwise gracefully falls back to transparent Demo Readiness Scoring.
    """
    if current_app:
        m_path = model_path or current_app.config.get("MODEL_PATH")
        p_path = preprocessor_path or current_app.config.get("PREPROCESSOR_PATH")
    else:
        base = Path(__file__).resolve().parent
        m_path = model_path or str(base / "trained_model.joblib")
        p_path = preprocessor_path or str(base / "preprocessor.joblib")

    model = load_model(m_path)
    preprocessor = load_model(p_path)

    if model is None or preprocessor is None:
        # Fallback to Demo Readiness Score
        return calculate_demo_readiness(student_data)

    try:
        X_df = extract_features_from_student(student_data)
        X_scaled = preprocessor.transform(X_df)

        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X_scaled)[0]
            # Class 1 probability represents readiness percentage
            placed_prob = probs[1] if len(probs) > 1 else probs[0]
            score = round(float(placed_prob) * 100.0, 1)
        else:
            pred = model.predict(X_scaled)[0]
            score = 85.0 if pred == 1 else 45.0

        category = get_category_from_score(score)

        # Highlight key factors
        factors = []
        cgpa = float(student_data.get("cgpa") or 0.0)
        backlogs = int(student_data.get("backlogs") or 0)
        if backlogs > 0:
            factors.append(f"{backlogs} active backlog(s) heavily suppresses model readiness score")
        if cgpa >= 7.5:
            factors.append(f"Strong CGPA ({cgpa:.2f}) positively influenced model classification")
        internships = student_data.get("internships") or []
        if len(internships) > 0:
            factors.append("Internship experience provided positive feature weighting")
        if not factors:
            factors.append("Evaluated across 11 standardized academic and technical feature metrics")

        return {
            "mode": "ML Model",
            "readiness_score": score,
            "readiness_category": category,
            "key_factors": "; ".join(factors),
            "breakdown": {
                "model_type": type(model).__name__,
                "predicted_probability": round(score / 100.0, 4)
            },
            "disclaimer": "This readiness assessment is generated via a trained Machine Learning model. Results are estimates and do not guarantee employment or selection."
        }
    except Exception as e:
        print(f"[Warning] ML prediction failed with error: {e}. Falling back to demo scoring.")
        demo_res = calculate_demo_readiness(student_data)
        demo_res["fallback_reason"] = str(e)
        return demo_res
