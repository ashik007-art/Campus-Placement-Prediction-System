"""Student profile, academic metrics, skills, and portfolio service operations."""
from werkzeug.security import generate_password_hash
from database.db import get_db, query_db, execute_db
from models.student import Student

class StudentService:

    @staticmethod
    def get_all_students(department=None, graduation_year=None, search=None):
        """Retrieve student list with optional filtering and search."""
        query = """
            SELECT s.id, s.user_id, s.student_id_number, s.department, s.graduation_year,
                   s.communication_level, s.aptitude_level, s.phone,
                   u.full_name, u.email,
                   a.cgpa, a.backlogs, a.tenth_percentage, a.twelfth_percentage, a.attendance_percentage
            FROM students s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN academic_details a ON s.id = a.student_id
            WHERE 1=1
        """
        params = []
        if department:
            query += " AND s.department = ?"
            params.append(department)
        if graduation_year:
            query += " AND s.graduation_year = ?"
            params.append(graduation_year)
        if search:
            query += " AND (u.full_name LIKE ? OR u.email LIKE ? OR s.student_id_number LIKE ?)"
            term = f"%{search.strip()}%"
            params.extend([term, term, term])

        query += " ORDER BY u.full_name ASC"
        rows = query_db(query, params)
        return [Student(dict(row)) for row in rows]

    @staticmethod
    def get_student_by_id(student_id):
        """Retrieve complete student entity including academic, skills, projects, and internships."""
        query = """
            SELECT s.id, s.user_id, s.student_id_number, s.department, s.graduation_year,
                   s.communication_level, s.aptitude_level, s.resume_url, s.phone, s.created_at,
                   u.full_name, u.email,
                   a.tenth_percentage, a.twelfth_percentage, a.cgpa, a.backlogs, a.attendance_percentage
            FROM students s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN academic_details a ON s.id = a.student_id
            WHERE s.id = ?
        """
        row = query_db(query, (student_id,), one=True)
        if not row:
            return None

        student_data = dict(row)

        # Retrieve student skills
        skills_query = """
            SELECT sk.id, sk.name, sk.category, ss.proficiency
            FROM student_skills ss
            JOIN skills sk ON ss.skill_id = sk.id
            WHERE ss.student_id = ?
            ORDER BY sk.name ASC
        """
        student_data["skills"] = [dict(r) for r in query_db(skills_query, (student_id,))]

        # Retrieve certifications
        cert_query = "SELECT * FROM certifications WHERE student_id = ? ORDER BY created_at DESC"
        student_data["certifications"] = [dict(r) for r in query_db(cert_query, (student_id,))]

        # Retrieve internships
        intern_query = "SELECT * FROM internships WHERE student_id = ? ORDER BY created_at DESC"
        student_data["internships"] = [dict(r) for r in query_db(intern_query, (student_id,))]

        # Retrieve projects
        proj_query = "SELECT * FROM projects WHERE student_id = ? ORDER BY created_at DESC"
        student_data["projects"] = [dict(r) for r in query_db(proj_query, (student_id,))]

        return Student(student_data)

    @staticmethod
    def get_student_by_user_id(user_id):
        """Retrieve student entity using user login ID."""
        row = query_db("SELECT id FROM students WHERE user_id = ?", (user_id,), one=True)
        if not row:
            return None
        return StudentService.get_student_by_id(row["id"])

    @staticmethod
    def create_student(full_name, email, password, student_id_number, department, graduation_year,
                       phone="", comm_level="Intermediate", apt_level="Intermediate",
                       tenth=75.0, twelfth=75.0, cgpa=7.0, backlogs=0, attendance=85.0):
        """Register a user, student record, and initial academic details in a single transaction."""
        db = get_db()
        try:
            # Check for existing email or student id
            existing_user = query_db("SELECT id FROM users WHERE email = ?", (email.strip(),), one=True)
            if existing_user:
                return False, "An account with this email address already exists."

            existing_id = query_db("SELECT id FROM students WHERE student_id_number = ?", (student_id_number.strip(),), one=True)
            if existing_id:
                return False, "Student ID Number is already registered."

            # 1. Insert user
            pwd_hash = generate_password_hash(password)
            cur = db.execute(
                "INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, 'student')",
                (full_name.strip(), email.strip().lower(), pwd_hash)
            )
            user_id = cur.lastrowid

            # 2. Insert student profile
            cur = db.execute("""
                INSERT INTO students (user_id, student_id_number, phone, department, graduation_year, communication_level, aptitude_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, student_id_number.strip().upper(), phone.strip(), department.strip(), int(graduation_year), comm_level, apt_level))
            student_id = cur.lastrowid

            # 3. Insert academic details
            db.execute("""
                INSERT INTO academic_details (student_id, tenth_percentage, twelfth_percentage, cgpa, backlogs, attendance_percentage)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (student_id, float(tenth), float(twelfth), float(cgpa), int(backlogs), float(attendance)))

            db.commit()
            return True, student_id
        except Exception as e:
            db.rollback()
            return False, f"Error creating student: {str(e)}"

    @staticmethod
    def update_student(student_id, full_name, email, department, graduation_year,
                       phone=None, comm_level=None, apt_level=None, resume_url=None,
                       tenth=None, twelfth=None, cgpa=None, backlogs=None, attendance=None):
        """Update student profile and academic details transactionally."""
        db = get_db()
        try:
            # Check email uniqueness against other users
            st = query_db("SELECT user_id FROM students WHERE id = ?", (student_id,), one=True)
            if not st:
                return False, "Student not found."

            user_id = st["user_id"]
            if email:
                dup = query_db("SELECT id FROM users WHERE email = ? AND id != ?", (email.strip().lower(), user_id), one=True)
                if dup:
                    return False, "Email is already taken by another account."
                db.execute("UPDATE users SET full_name = ?, email = ? WHERE id = ?", (full_name.strip(), email.strip().lower(), user_id))
            else:
                db.execute("UPDATE users SET full_name = ? WHERE id = ?", (full_name.strip(), user_id))

            # Update student record
            db.execute("""
                UPDATE students
                SET department = ?, graduation_year = ?, phone = ?, communication_level = ?, aptitude_level = ?, resume_url = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (department, int(graduation_year), phone, comm_level, apt_level, resume_url, student_id))

            # Update academic details if provided
            if tenth is not None and twelfth is not None and cgpa is not None:
                db.execute("""
                    UPDATE academic_details
                    SET tenth_percentage = ?, twelfth_percentage = ?, cgpa = ?, backlogs = ?, attendance_percentage = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE student_id = ?
                """, (float(tenth), float(twelfth), float(cgpa), int(backlogs or 0), float(attendance or 85.0), student_id))

            db.commit()
            return True, "Profile updated successfully."
        except Exception as e:
            db.rollback()
            return False, f"Failed to update student: {str(e)}"

    @staticmethod
    def delete_student(student_id):
        """Delete student and related user account cascading."""
        db = get_db()
        try:
            st = query_db("SELECT user_id FROM students WHERE id = ?", (student_id,), one=True)
            if not st:
                return False, "Student record not found."
            # Deleting the user row will cascade delete student, academics, applications, etc.
            db.execute("DELETE FROM users WHERE id = ?", (st["user_id"],))
            db.commit()
            return True, "Student deleted successfully."
        except Exception as e:
            db.rollback()
            return False, f"Deletion failed: {str(e)}"

    # --- Skills Management ---
    @staticmethod
    def get_all_master_skills():
        return [dict(r) for r in query_db("SELECT * FROM skills ORDER BY category, name ASC")]

    @staticmethod
    def add_student_skill(student_id, skill_id, proficiency="Intermediate"):
        try:
            execute_db("""
                INSERT INTO student_skills (student_id, skill_id, proficiency)
                VALUES (?, ?, ?)
                ON CONFLICT(student_id, skill_id) DO UPDATE SET proficiency=excluded.proficiency
            """, (student_id, skill_id, proficiency))
            return True, "Skill updated."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def remove_student_skill(student_id, skill_id):
        try:
            execute_db("DELETE FROM student_skills WHERE student_id = ? AND skill_id = ?", (student_id, skill_id))
            return True, "Skill removed."
        except Exception as e:
            return False, str(e)

    # --- Certifications, Internships, Projects ---
    @staticmethod
    def add_certification(student_id, title, issuing_org, issue_date=None, credential_url=None):
        try:
            cid = execute_db("""
                INSERT INTO certifications (student_id, title, issuing_organization, issue_date, credential_url)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, title.strip(), issuing_org.strip(), issue_date, credential_url))
            return True, cid
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_certification(cert_id, student_id=None):
        try:
            if student_id:
                execute_db("DELETE FROM certifications WHERE id = ? AND student_id = ?", (cert_id, student_id))
            else:
                execute_db("DELETE FROM certifications WHERE id = ?", (cert_id,))
            return True, "Certification deleted."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def add_internship(student_id, company_name, role, duration_months, description=None, start_date=None, end_date=None):
        try:
            iid = execute_db("""
                INSERT INTO internships (student_id, company_name, role, duration_months, description, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (student_id, company_name.strip(), role.strip(), int(duration_months), description, start_date, end_date))
            return True, iid
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_internship(internship_id, student_id=None):
        try:
            if student_id:
                execute_db("DELETE FROM internships WHERE id = ? AND student_id = ?", (internship_id, student_id))
            else:
                execute_db("DELETE FROM internships WHERE id = ?", (internship_id,))
            return True, "Internship deleted."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def add_project(student_id, title, tech_stack=None, description=None, github_url=None):
        try:
            pid = execute_db("""
                INSERT INTO projects (student_id, title, tech_stack, description, github_url)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, title.strip(), tech_stack, description, github_url))
            return True, pid
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_project(project_id, student_id=None):
        try:
            if student_id:
                execute_db("DELETE FROM projects WHERE id = ? AND student_id = ?", (project_id, student_id))
            else:
                execute_db("DELETE FROM projects WHERE id = ?", (project_id,))
            return True, "Project deleted."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_distinct_departments():
        rows = query_db("SELECT DISTINCT department FROM students WHERE department IS NOT NULL AND department != '' ORDER BY department ASC")
        return [r["department"] for r in rows]

    @staticmethod
    def get_distinct_graduation_years():
        rows = query_db("SELECT DISTINCT graduation_year FROM students WHERE graduation_year IS NOT NULL ORDER BY graduation_year DESC")
        return [r["graduation_year"] for r in rows]
