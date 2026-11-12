"""Feature extraction and preprocessing pipeline."""
import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "tenth_percentage",
    "twelfth_percentage",
    "cgpa",
    "backlogs",
    "attendance_percentage",
    "communication_score",
    "aptitude_score",
    "internship_count",
    "project_count",
    "certification_count",
    "skill_count"
]

LEVEL_MAPPING = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3
}

def map_level_to_score(level_str: str) -> int:
    """Map proficiency text to integer score."""
    if not level_str:
        return 2
    return LEVEL_MAPPING.get(str(level_str).strip().lower(), 2)

def extract_features_from_student(student_dict: dict) -> pd.DataFrame:
    """
    Extract a single-row DataFrame aligned with FEATURE_COLUMNS from a student dictionary.
    Safe against missing keys and None values.
    """
    tenth = float(student_dict.get("tenth_percentage") or 0.0)
    twelfth = float(student_dict.get("twelfth_percentage") or 0.0)
    cgpa = float(student_dict.get("cgpa") or 0.0)
    backlogs = int(student_dict.get("backlogs") or 0)
    attendance = float(student_dict.get("attendance_percentage") or 85.0)
    
    comm = map_level_to_score(student_dict.get("communication_level"))
    apt = map_level_to_score(student_dict.get("aptitude_level"))

    internships = student_dict.get("internships") or []
    internship_count = len(internships) if isinstance(internships, list) else int(student_dict.get("internship_count") or 0)

    projects = student_dict.get("projects") or []
    project_count = len(projects) if isinstance(projects, list) else int(student_dict.get("project_count") or 0)

    certifications = student_dict.get("certifications") or []
    certification_count = len(certifications) if isinstance(certifications, list) else int(student_dict.get("certification_count") or 0)

    skills = student_dict.get("skills") or []
    skill_count = len(skills) if isinstance(skills, list) else int(student_dict.get("skill_count") or 0)

    row = {
        "tenth_percentage": tenth,
        "twelfth_percentage": twelfth,
        "cgpa": cgpa,
        "backlogs": backlogs,
        "attendance_percentage": attendance,
        "communication_score": comm,
        "aptitude_score": apt,
        "internship_count": internship_count,
        "project_count": project_count,
        "certification_count": certification_count,
        "skill_count": skill_count
    }

    return pd.DataFrame([row], columns=FEATURE_COLUMNS)
