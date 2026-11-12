"""Database seed script with clearly labeled demonstration records."""
import os
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load env variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DB_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "database" / "placement_system.db"))

def seed_database(db_path=None):
    if db_path is None:
        db_path = DB_PATH

    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # Read and apply schema
    schema_path = BASE_DIR / "database" / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        cur.executescript(f.read())

    print("[*] Database schema initialized.")

    # 1. Admin User
    admin_name = os.environ.get("ADMIN_NAME", "Placement Officer Admin")
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@campus.edu")
    admin_password = os.environ.get("ADMIN_PASSWORD", "AdminSecurePass@2026")
    admin_hash = generate_password_hash(admin_password)

    cur.execute("SELECT id FROM users WHERE email = ?", (admin_email,))
    admin_row = cur.fetchone()
    if not admin_row:
        cur.execute(
            "INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, 'admin')",
            (admin_name, admin_email, admin_hash)
        )
        print(f"[+] Admin created: {admin_email}")
    else:
        print(f"[-] Admin already exists: {admin_email}")

    # 2. Master Skills
    skills_data = [
        ("Python", "Programming"),
        ("Java", "Programming"),
        ("C++", "Programming"),
        ("SQL", "Database"),
        ("Machine Learning", "Technical"),
        ("Data Structures", "Technical"),
        ("Web Development", "Technical"),
        ("Cloud Computing", "Technical"),
        ("Git", "Technical"),
        ("Docker", "Technical"),
        ("React", "Technical"),
        ("Spring Boot", "Technical"),
        ("Communication", "Soft Skill"),
        ("Problem Solving", "Soft Skill"),
        ("Aptitude", "Soft Skill"),
    ]
    skill_map = {}
    for name, cat in skills_data:
        cur.execute("SELECT id FROM skills WHERE name = ?", (name,))
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO skills (name, category) VALUES (?, ?)", (name, cat))
            skill_map[name] = cur.lastrowid
        else:
            skill_map[name] = row[0]
    print(f"[+] Seeded {len(skill_map)} master skills.")

    # 3. Companies
    companies_data = [
        ("TechCorp Solutions", "Information Technology", "Global enterprise IT consulting and software engineering firm.", "https://techcorp.example.com", "Bangalore, India"),
        ("Innovate AI Labs", "Artificial Intelligence & Analytics", "Next-gen AI research and data intelligence solutions.", "https://innovateai.example.com", "Hyderabad, India"),
        ("CloudScale Networks", "Cloud & Infrastructure", "Hyperscale cloud orchestration and networking platforms.", "https://cloudscale.example.com", "Pune, India"),
        ("FinEdge Technologies", "Financial Technology", "High-frequency algorithmic trading and fintech banking services.", "https://finedge.example.com", "Mumbai, India")
    ]
    company_map = {}
    for cname, ind, desc, web, loc in companies_data:
        cur.execute("SELECT id FROM companies WHERE name = ?", (cname,))
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO companies (name, industry, description, website, location) VALUES (?, ?, ?, ?, ?)",
                        (cname, ind, desc, web, loc))
            company_map[cname] = cur.lastrowid
        else:
            company_map[cname] = row[0]
    print(f"[+] Seeded {len(company_map)} companies.")

    # 4. Job Roles
    job_roles_data = [
        ("TechCorp Solutions", "Software Development Engineer", 7.0, 0, "8.5 LPA", "Full-stack software engineering and backend systems design.", ["Python", "Java", "Data Structures", "SQL"]),
        ("Innovate AI Labs", "Machine Learning Associate", 7.5, 0, "10.0 LPA", "Build, evaluate, and deploy machine learning models in production.", ["Python", "Machine Learning", "SQL", "Problem Solving"]),
        ("CloudScale Networks", "Cloud DevOps Engineer", 6.5, 1, "7.2 LPA", "Containerization, cloud infrastructure automation, and CI/CD pipelines.", ["Cloud Computing", "Docker", "Git"]),
        ("FinEdge Technologies", "Associate Backend Analyst", 6.0, 1, "6.5 LPA", "Financial transaction processing and database optimization.", ["Java", "SQL", "Problem Solving"])
    ]
    job_role_map = {}
    for cname, rname, min_cgpa, max_bl, pkg, rdesc, req_skills in job_roles_data:
        cid = company_map[cname]
        cur.execute("SELECT id FROM job_roles WHERE company_id = ? AND role_name = ?", (cid, rname))
        row = cur.fetchone()
        if not row:
            cur.execute("""
                INSERT INTO job_roles (company_id, role_name, min_cgpa, max_backlogs, salary_package, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cid, rname, min_cgpa, max_bl, pkg, rdesc))
            j_id = cur.lastrowid
        else:
            j_id = row[0]
        job_role_map[rname] = j_id

        # Insert required skills
        for s_name in req_skills:
            if s_name in skill_map:
                cur.execute("SELECT id FROM job_required_skills WHERE job_role_id = ? AND skill_id = ?", (j_id, skill_map[s_name]))
                if not cur.fetchone():
                    cur.execute("INSERT INTO job_required_skills (job_role_id, skill_id, is_mandatory) VALUES (?, ?, 1)",
                                (j_id, skill_map[s_name]))
    print(f"[+] Seeded {len(job_role_map)} job roles with skill mappings.")

    # 5. Placement Drives
    drives_data = [
        ("TechCorp Solutions", "Software Development Engineer", "TechCorp Annual Campus Drive 2026", "2026-11-15", "2026-11-05", "Online Coding Test -> Technical Interview -> HR Round", "Upcoming"),
        ("Innovate AI Labs", "Machine Learning Associate", "Innovate AI Hack-to-Hire 2026", "2026-10-25", "2026-10-18", "Data Science Assessment -> Architecture Review -> HR", "Upcoming"),
        ("CloudScale Networks", "Cloud DevOps Engineer", "CloudScale Fall Drive 2026", "2026-10-01", "2026-09-25", "Hands-on Lab -> System Design Interview -> Offer", "Ongoing"),
        ("FinEdge Technologies", "Associate Backend Analyst", "FinEdge National Campus Challenge", "2026-09-15", "2026-09-10", "Aptitude -> Core Java Coding -> Management Discussion", "Completed")
    ]
    drive_map = {}
    for cname, rname, title, d_date, d_dead, sel_proc, stat in drives_data:
        cid = company_map[cname]
        jid = job_role_map[rname]
        cur.execute("SELECT id FROM placement_drives WHERE company_id = ? AND job_role_id = ? AND title = ?", (cid, jid, title))
        row = cur.fetchone()
        if not row:
            cur.execute("""
                INSERT INTO placement_drives (company_id, job_role_id, title, drive_date, application_deadline, selection_process, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cid, jid, title, d_date, d_dead, sel_proc, stat))
            drive_map[title] = cur.lastrowid
        else:
            drive_map[title] = row[0]
    print(f"[+] Seeded {len(drive_map)} placement drives.")

    # 6. Sample Students
    students_seed = [
        {
            "name": "Priya Sharma",
            "email": "priya.sharma@campus.edu",
            "password": "StudentPass@2026",
            "student_id": "STU2026001",
            "phone": "+91 98765 43210",
            "dept": "Computer Science & Engineering",
            "year": 2026,
            "comm": "Advanced",
            "apt": "Advanced",
            "tenth": 92.5,
            "twelfth": 89.0,
            "cgpa": 8.85,
            "backlogs": 0,
            "attendance": 94.0,
            "skills": [("Python", "Advanced"), ("Machine Learning", "Advanced"), ("SQL", "Intermediate"), ("Data Structures", "Advanced"), ("Problem Solving", "Advanced")],
            "internships": [("TechCorp Solutions", "Software Engineering Intern", 3, "Developed automated microservice reporting tools using Python and Flask.", "2025-06-01", "2025-08-31")],
            "projects": [("Campus Placement Readiness System", "Python, Flask, Scikit-learn, SQLite", "Built an end-to-end web portal predicting student placement readiness.", "https://github.com/priyasharma/campus-placement")],
            "certifications": [("AWS Certified Cloud Practitioner", "Amazon Web Services", "2025-04-10", "https://aws.amazon.com/verify")]
        },
        {
            "name": "Rahul Verma",
            "email": "rahul.verma@campus.edu",
            "password": "StudentPass@2026",
            "student_id": "STU2026002",
            "phone": "+91 98765 43211",
            "dept": "Information Technology",
            "year": 2026,
            "comm": "Intermediate",
            "apt": "Intermediate",
            "tenth": 81.0,
            "twelfth": 78.5,
            "cgpa": 7.30,
            "backlogs": 0,
            "attendance": 88.0,
            "skills": [("Java", "Intermediate"), ("Web Development", "Intermediate"), ("SQL", "Intermediate"), ("Git", "Intermediate")],
            "internships": [],
            "projects": [("E-Commerce Portal", "Java, Spring Boot, MySQL", "Designed a responsive online storefront with inventory management.", "https://github.com/rahulverma/ecommerce-store")],
            "certifications": [("Oracle Certified Associate - Java SE", "Oracle", "2025-02-15", "https://oracle.com/verify")]
        },
        {
            "name": "Ananya Patel",
            "email": "ananya.patel@campus.edu",
            "password": "StudentPass@2026",
            "student_id": "STU2026003",
            "phone": "+91 98765 43212",
            "dept": "Electronics & Communication",
            "year": 2026,
            "comm": "Beginner",
            "apt": "Intermediate",
            "tenth": 72.0,
            "twelfth": 68.0,
            "cgpa": 6.20,
            "backlogs": 2,
            "attendance": 76.5,
            "skills": [("C++", "Intermediate"), ("Git", "Beginner")],
            "internships": [],
            "projects": [("IoT Weather Station", "C++, Arduino, Sensors", "Built ambient temperature and humidity tracking sensor network.", "https://github.com/ananyapatel/iot-weather")],
            "certifications": []
        },
        {
            "name": "Vikram Singh",
            "email": "vikram.singh@campus.edu",
            "password": "StudentPass@2026",
            "student_id": "STU2026004",
            "phone": "+91 98765 43213",
            "dept": "Computer Science & Engineering",
            "year": 2026,
            "comm": "Advanced",
            "apt": "Intermediate",
            "tenth": 85.0,
            "twelfth": 83.0,
            "cgpa": 7.90,
            "backlogs": 0,
            "attendance": 91.0,
            "skills": [("Cloud Computing", "Advanced"), ("Docker", "Intermediate"), ("Git", "Advanced"), ("Python", "Intermediate")],
            "internships": [("CloudScale Networks", "DevOps Trainee", 2, "Automated Docker container builds and CI/CD pipelines.", "2025-07-01", "2025-08-31")],
            "projects": [("Kubernetes Microservices Cluster", "Docker, Kubernetes, Terraform", "Configured resilient auto-scaling cluster deployment.", "https://github.com/vikramsingh/k8s-cluster")],
            "certifications": [("Docker Certified Associate", "Docker Inc.", "2025-05-12", "https://docker.com/verify")]
        }
    ]

    student_id_map = {}
    for s in students_seed:
        # User account
        cur.execute("SELECT id FROM users WHERE email = ?", (s["email"],))
        u_row = cur.fetchone()
        if not u_row:
            cur.execute("INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, 'student')",
                        (s["name"], s["email"], generate_password_hash(s["password"])))
            uid = cur.lastrowid
        else:
            uid = u_row[0]

        # Student record
        cur.execute("SELECT id FROM students WHERE user_id = ?", (uid,))
        st_row = cur.fetchone()
        if not st_row:
            cur.execute("""
                INSERT INTO students (user_id, student_id_number, phone, department, graduation_year, communication_level, aptitude_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (uid, s["student_id"], s["phone"], s["dept"], s["year"], s["comm"], s["apt"]))
            sid = cur.lastrowid
        else:
            sid = st_row[0]
        student_id_map[s["name"]] = sid

        # Academic record
        cur.execute("SELECT id FROM academic_details WHERE student_id = ?", (sid,))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO academic_details (student_id, tenth_percentage, twelfth_percentage, cgpa, backlogs, attendance_percentage)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sid, s["tenth"], s["twelfth"], s["cgpa"], s["backlogs"], s["attendance"]))

        # Skills
        for sk_name, prof in s["skills"]:
            if sk_name in skill_map:
                cur.execute("SELECT id FROM student_skills WHERE student_id = ? AND skill_id = ?", (sid, skill_map[sk_name]))
                if not cur.fetchone():
                    cur.execute("INSERT INTO student_skills (student_id, skill_id, proficiency) VALUES (?, ?, ?)",
                                (sid, skill_map[sk_name], prof))

        # Internships
        for cname, role, dur, desc, s_dt, e_dt in s["internships"]:
            cur.execute("SELECT id FROM internships WHERE student_id = ? AND company_name = ?", (sid, cname))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO internships (student_id, company_name, role, duration_months, description, start_date, end_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (sid, cname, role, dur, desc, s_dt, e_dt))

        # Projects
        for ptitle, tech, pdesc, gh in s["projects"]:
            cur.execute("SELECT id FROM projects WHERE student_id = ? AND title = ?", (sid, ptitle))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO projects (student_id, title, tech_stack, description, github_url)
                    VALUES (?, ?, ?, ?, ?)
                """, (sid, ptitle, tech, pdesc, gh))

        # Certifications
        for ctitle, org, idt, curl in s["certifications"]:
            cur.execute("SELECT id FROM certifications WHERE student_id = ? AND title = ?", (sid, ctitle))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO certifications (student_id, title, issuing_organization, issue_date, credential_url)
                    VALUES (?, ?, ?, ?, ?)
                """, (sid, ctitle, org, idt, curl))

    print(f"[+] Seeded {len(student_id_map)} student profiles with full academic, skill, and portfolio records.")

    # 7. Applications
    priya_id = student_id_map["Priya Sharma"]
    rahul_id = student_id_map["Rahul Verma"]
    vikram_id = student_id_map["Vikram Singh"]
    
    app_seeds = [
        (drive_map["TechCorp Annual Campus Drive 2026"], priya_id, "Selected", "Cleared technical coding and managerial interviews with distinction."),
        (drive_map["Innovate AI Hack-to-Hire 2026"], priya_id, "Interview", "Shortlisted for Round 2 live algorithm presentation."),
        (drive_map["TechCorp Annual Campus Drive 2026"], rahul_id, "Shortlisted", "Completed initial screening assessment."),
        (drive_map["CloudScale Fall Drive 2026"], vikram_id, "Selected", "Offered Cloud DevOps Associate position.")
    ]
    for did, sid, stat, notes in app_seeds:
        cur.execute("SELECT id FROM applications WHERE drive_id = ? AND student_id = ?", (did, sid))
        if not cur.fetchone():
            cur.execute("INSERT INTO applications (drive_id, student_id, status, notes) VALUES (?, ?, ?, ?)",
                        (did, sid, stat, notes))

    # 8. Sample Predictions & Recommendations
    cur.execute("SELECT id FROM predictions WHERE student_id = ?", (priya_id,))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO predictions (student_id, mode, readiness_score, readiness_category, key_factors)
            VALUES (?, 'Demo Readiness Score', 92.5, 'High Readiness', 'Strong CGPA (8.85), 0 backlogs, completed internship, high skill breadth.')
        """, (priya_id,))
        cur.execute("""
            INSERT INTO recommendations (student_id, category, title, description, priority)
            VALUES (?, 'General', 'Prepare System Design Fundamentals', 'Review scalable distributed system architectures for top-tier product company rounds.', 'Low')
        """, (priya_id,))

    conn.commit()
    conn.close()
    print("[*] Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
