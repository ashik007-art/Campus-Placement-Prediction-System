"""Skill Gap Analysis and Rule-Based Recommendations Engine."""
from database.db import get_db, query_db, execute_db
from models.recommendation import RecommendationRecord

class RecommendationService:

    @staticmethod
    def analyze_skill_gap(student_id, job_role_id=None, drive_id=None):
        """
        Compare student's skills against job role or drive required skills.
        Calculates exact match percentage, lists matched and missing skills,
        and safely avoids division-by-zero errors.
        """
        # Fetch student skills
        st_skills = query_db("""
            SELECT s.id, s.name, ss.proficiency
            FROM student_skills ss
            JOIN skills s ON ss.skill_id = s.id
            WHERE ss.student_id = ?
        """, (student_id,))
        student_skill_names = {s["name"].strip().lower(): s["name"] for s in st_skills}

        # Resolve job_role_id if drive_id is provided
        if drive_id and not job_role_id:
            drive_row = query_db("SELECT job_role_id FROM placement_drives WHERE id = ?", (drive_id,), one=True)
            if drive_row:
                job_role_id = drive_row["job_role_id"]

        if not job_role_id:
            return {
                "total_required": 0,
                "matched_count": 0,
                "match_percentage": 0.0,
                "matched_skills": [],
                "missing_skills": [],
                "recommendation_summary": "Select a specific job role or placement drive to analyze skill gaps."
            }

        # Fetch required skills
        req_skills = query_db("""
            SELECT s.id, s.name, s.category, jrs.is_mandatory
            FROM job_required_skills jrs
            JOIN skills s ON jrs.skill_id = s.id
            WHERE jrs.job_role_id = ?
        """, (job_role_id,))

        total_req = len(req_skills)
        if total_req == 0:
            return {
                "total_required": 0,
                "matched_count": 0,
                "match_percentage": 100.0,  # No requirements means 100% compliant
                "matched_skills": list(student_skill_names.values()),
                "missing_skills": [],
                "recommendation_summary": "This role does not specify mandatory required skills."
            }

        matched_skills = []
        missing_skills = []

        for req in req_skills:
            norm_name = req["name"].strip().lower()
            if norm_name in student_skill_names:
                matched_skills.append({
                    "id": req["id"],
                    "name": req["name"],
                    "category": req["category"],
                    "is_mandatory": bool(req["is_mandatory"])
                })
            else:
                missing_skills.append({
                    "id": req["id"],
                    "name": req["name"],
                    "category": req["category"],
                    "is_mandatory": bool(req["is_mandatory"])
                })

        match_pct = round((len(matched_skills) / total_req) * 100.0, 1)

        summary = f"Student matches {len(matched_skills)} of {total_req} required competencies ({match_pct}% match)."
        if missing_skills:
            missing_names = ", ".join([m["name"] for m in missing_skills[:3]])
            summary += f" Recommended focus: Acquire proficiency in {missing_names}."

        return {
            "total_required": total_req,
            "matched_count": len(matched_skills),
            "match_percentage": match_pct,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "recommendation_summary": summary
        }

    @staticmethod
    def generate_recommendations_for_student(student_id):
        """
        Generate actionable recommendations using explicit rules based on student information.
        Does not invent real courses, job openings, or certifications.
        """
        # Fetch student and academics
        st = query_db("""
            SELECT s.*, u.full_name, a.cgpa, a.backlogs, a.attendance_percentage, a.tenth_percentage, a.twelfth_percentage
            FROM students s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN academic_details a ON s.id = a.student_id
            WHERE s.id = ?
        """, (student_id,), one=True)
        if not st:
            return []

        cgpa = float(st["cgpa"] or 0.0)
        backlogs = int(st["backlogs"] or 0)
        attendance = float(st["attendance_percentage"] or 85.0)
        comm = str(st["communication_level"] or "Intermediate").lower()
        apt = str(st["aptitude_level"] or "Intermediate").lower()

        # Counts
        skill_cnt = query_db("SELECT COUNT(*) as cnt FROM student_skills WHERE student_id = ?", (student_id,), one=True)["cnt"]
        project_cnt = query_db("SELECT COUNT(*) as cnt FROM projects WHERE student_id = ?", (student_id,), one=True)["cnt"]
        intern_cnt = query_db("SELECT COUNT(*) as cnt FROM internships WHERE student_id = ?", (student_id,), one=True)["cnt"]
        cert_cnt = query_db("SELECT COUNT(*) as cnt FROM certifications WHERE student_id = ?", (student_id,), one=True)["cnt"]

        recs = []

        # 1. Backlogs (Highest priority)
        if backlogs > 0:
            recs.append({
                "category": "Academic",
                "title": "Clear Active Backlog Papers Immediately",
                "description": f"You currently have {backlogs} active backlog(s). Most campus recruitment partners enforce a strict zero-backlog policy during initial shortlisting.",
                "priority": "High"
            })

        # 2. CGPA
        if cgpa < 6.5:
            recs.append({
                "category": "Academic",
                "title": "Improve Core Semester CGPA",
                "description": f"Current CGPA is {cgpa:.2f}. Raising your cumulative score above 7.0 will unlock eligibility for over 70% of participating companies.",
                "priority": "High"
            })
        elif cgpa < 7.5:
            recs.append({
                "category": "Academic",
                "title": "Target 8.0+ CGPA for Tier-1 Roles",
                "description": f"Your CGPA is {cgpa:.2f}. Pushing your GPA past 7.5 - 8.0 opens premium product engineering and data science roles.",
                "priority": "Medium"
            })

        # 3. Attendance
        if attendance < 75.0:
            recs.append({
                "category": "Academic",
                "title": "Restore Minimum 75% Attendance",
                "description": f"Current attendance is {attendance:.1f}%. College regulations and campus drive hall tickets require at least 75% attendance.",
                "priority": "High"
            })

        # 4. Technical Skills
        if skill_cnt < 3:
            recs.append({
                "category": "Skills",
                "title": "Expand Core Technical Skill Set",
                "description": "You currently have fewer than 3 verified skills recorded. Add core proficiencies such as SQL, Data Structures, Git, and a modern programming language.",
                "priority": "High"
            })
        elif skill_cnt < 5:
            recs.append({
                "category": "Skills",
                "title": "Acquire Specialized Industry Skills",
                "description": "Complement your core programming skills with in-demand frameworks like React, Spring Boot, Docker, or Cloud Computing.",
                "priority": "Medium"
            })

        # 5. Internships
        if intern_cnt == 0:
            recs.append({
                "category": "Experience",
                "title": "Seek Practical Internship or Apprenticeship",
                "description": "Candidates with at least one verified industry internship demonstrate applied teamwork and enjoy substantially higher selection odds.",
                "priority": "High"
            })

        # 6. Projects
        if project_cnt < 2:
            recs.append({
                "category": "Projects",
                "title": "Build and Deploy Practical Software Projects",
                "description": "Develop and document full-stack or domain-specific projects with public Git repositories to showcase during technical interview rounds.",
                "priority": "Medium"
            })

        # 7. Soft skills & Aptitude
        if apt in ("beginner", "intermediate"):
            recs.append({
                "category": "Aptitude",
                "title": "Practice Quantitative & Logical Aptitude Assessments",
                "description": "Consistently solve quantitative aptitude, logical reasoning, and data interpretation problems to clear preliminary online screening exams.",
                "priority": "Medium"
            })

        if comm in ("beginner", "intermediate"):
            recs.append({
                "category": "Communication",
                "title": "Participate in Mock Technical & HR Interviews",
                "description": "Refine technical explanation, articulation of project architecture, and behavioral interview responses through mock peer interviews.",
                "priority": "Medium"
            })

        # Clear previous recommendations and save new set
        db = get_db()
        db.execute("DELETE FROM recommendations WHERE student_id = ?", (student_id,))
        for r in recs:
            db.execute("""
                INSERT INTO recommendations (student_id, category, title, description, priority)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, r["category"], r["title"], r["description"], r["priority"]))
        db.commit()

        return RecommendationService.get_student_recommendations(student_id)

    @staticmethod
    def get_student_recommendations(student_id):
        rows = query_db("""
            SELECT * FROM recommendations
            WHERE student_id = ?
            ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, created_at DESC
        """, (student_id,))
        return [RecommendationRecord(dict(r)) for r in rows]
