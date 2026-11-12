"""Company and Job Role service operations."""
from database.db import get_db, query_db, execute_db
from models.company import Company, JobRole

class CompanyService:

    @staticmethod
    def get_all_companies(search=None, industry=None):
        query = "SELECT * FROM companies WHERE 1=1"
        params = []
        if industry:
            query += " AND industry = ?"
            params.append(industry)
        if search:
            query += " AND (name LIKE ? OR description LIKE ? OR location LIKE ?)"
            term = f"%{search.strip()}%"
            params.extend([term, term, term])
        query += " ORDER BY name ASC"

        rows = query_db(query, params)
        companies = []
        for r in rows:
            comp = Company(dict(r))
            comp.job_roles = CompanyService.get_job_roles_by_company(comp.id)
            companies.append(comp)
        return companies

    @staticmethod
    def get_company_by_id(company_id):
        row = query_db("SELECT * FROM companies WHERE id = ?", (company_id,), one=True)
        if not row:
            return None
        comp = Company(dict(row))
        comp.job_roles = CompanyService.get_job_roles_by_company(comp.id)
        return comp

    @staticmethod
    def create_company(name, industry, description="", website="", location=""):
        try:
            existing = query_db("SELECT id FROM companies WHERE name = ?", (name.strip(),), one=True)
            if existing:
                return False, f"Company '{name}' already exists."
            cid = execute_db("""
                INSERT INTO companies (name, industry, description, website, location)
                VALUES (?, ?, ?, ?, ?)
            """, (name.strip(), industry.strip(), description.strip(), website.strip(), location.strip()))
            return True, cid
        except Exception as e:
            return False, f"Failed to add company: {str(e)}"

    @staticmethod
    def update_company(company_id, name, industry, description="", website="", location=""):
        try:
            existing = query_db("SELECT id FROM companies WHERE name = ? AND id != ?", (name.strip(), company_id), one=True)
            if existing:
                return False, f"Another company with name '{name}' already exists."
            execute_db("""
                UPDATE companies
                SET name = ?, industry = ?, description = ?, website = ?, location = ?
                WHERE id = ?
            """, (name.strip(), industry.strip(), description.strip(), website.strip(), location.strip(), company_id))
            return True, "Company updated successfully."
        except Exception as e:
            return False, f"Failed to update company: {str(e)}"

    @staticmethod
    def delete_company(company_id):
        try:
            execute_db("DELETE FROM companies WHERE id = ?", (company_id,))
            return True, "Company deleted successfully."
        except Exception as e:
            return False, f"Failed to delete company: {str(e)}"

    @staticmethod
    def get_distinct_industries():
        rows = query_db("SELECT DISTINCT industry FROM companies WHERE industry IS NOT NULL ORDER BY industry ASC")
        return [r["industry"] for r in rows]

    # --- Job Roles ---
    @staticmethod
    def get_job_roles_by_company(company_id):
        rows = query_db("""
            SELECT j.*, c.name as company_name
            FROM job_roles j
            JOIN companies c ON j.company_id = c.id
            WHERE j.company_id = ?
            ORDER BY j.role_name ASC
        """, (company_id,))
        roles = []
        for r in rows:
            jr = JobRole(dict(r))
            jr.required_skills = CompanyService.get_job_role_required_skills(jr.id)
            roles.append(jr)
        return roles

    @staticmethod
    def get_job_role_by_id(job_role_id):
        row = query_db("""
            SELECT j.*, c.name as company_name
            FROM job_roles j
            JOIN companies c ON j.company_id = c.id
            WHERE j.id = ?
        """, (job_role_id,), one=True)
        if not row:
            return None
        jr = JobRole(dict(row))
        jr.required_skills = CompanyService.get_job_role_required_skills(jr.id)
        return jr

    @staticmethod
    def get_job_role_required_skills(job_role_id):
        rows = query_db("""
            SELECT s.id, s.name, s.category, jrs.is_mandatory
            FROM job_required_skills jrs
            JOIN skills s ON jrs.skill_id = s.id
            WHERE jrs.job_role_id = ?
            ORDER BY s.name ASC
        """, (job_role_id,))
        return [dict(r) for r in rows]

    @staticmethod
    def create_job_role(company_id, role_name, min_cgpa, max_backlogs, salary_package, description="", required_skill_ids=None):
        db = get_db()
        try:
            cur = db.execute("""
                INSERT INTO job_roles (company_id, role_name, min_cgpa, max_backlogs, salary_package, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, role_name.strip(), float(min_cgpa), int(max_backlogs), salary_package.strip(), description.strip()))
            role_id = cur.lastrowid

            if required_skill_ids:
                for sid in required_skill_ids:
                    db.execute("INSERT OR IGNORE INTO job_required_skills (job_role_id, skill_id, is_mandatory) VALUES (?, ?, 1)",
                               (role_id, int(sid)))
            db.commit()
            return True, role_id
        except Exception as e:
            db.rollback()
            return False, f"Failed to create job role: {str(e)}"

    @staticmethod
    def delete_job_role(job_role_id):
        try:
            execute_db("DELETE FROM job_roles WHERE id = ?", (job_role_id,))
            return True, "Job role deleted."
        except Exception as e:
            return False, str(e)
