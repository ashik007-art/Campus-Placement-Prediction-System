# Campus Placement Prediction System

A comprehensive, full-stack academic web application designed for students, faculty coordinators, and placement officers to analyze undergraduate academic metrics, technical skill profiles, internships, corporate eligibility criteria, and machine-learning-driven placement readiness.

---

## 1. Key Features

- **Role-Based Authentication & Authorization:**
  - Secure registration and login with Werkzeug password hashing.
  - Role-based access control (RBAC) separating **Students** and **Administrators**.
  - Server-side validation and session security with CSRF verification.
- **Student Profile & Portfolio Management:**
  - Manage 10th, 12th/diploma, and undergraduate CGPA, backlogs, and attendance.
  - Relational portfolios: Technical skills, verified certifications, internships, and project repositories.
  - Profile completion scoring tracker.
- **Corporate Recruiter & Job Role Management:**
  - Manage company directory with industry sectors, descriptions, and locations.
  - Configurable job roles with minimum CGPA thresholds, maximum backlogs, salary packages (CTC), and required skills.
- **Campus Placement Drives & Applications:**
  - Schedule placement drives with application deadlines and selection rounds.
  - Automated server-side eligibility checks (CGPA and backlogs).
  - Application lifecycle tracking (`Applied`, `Shortlisted`, `Interview`, `Selected`, `Rejected`).
  - Prevention of duplicate applications.
- **Dual-Engine Placement Readiness Prediction:**
  - **Machine Learning Mode:** Scikit-learn Random Forest classifier trained on 11 normalized academic and experience indicators without data leakage.
  - **Demo Readiness Scoring:** Transparent rule-based fallback heuristic when no trained model is present.
  - Categorization into *High Readiness*, *Moderate Readiness*, and *Needs Improvement*.
- **Skill Gap Analysis:**
  - Real-time comparison between student competencies and target job role requirements.
  - Percentage match calculation `(Matching / Total) * 100` with division-by-zero protection.
  - Identification of missing required skills.
- **Personalized Recommendations:**
  - Rule-based action plans targeting identified academic deficits, backlogs, skill stack depth, and internship experience.
- **Institutional Reports & Analytics:**
  - Department-wise placement rate and average CGPA metrics.
  - Company selection tallies and drive conversion funnels.
  - One-click CSV report export.
- **Formal Semantic Ontology:**
  - W3C RDF/OWL Turtle ontology (`campus_placement_ontology.ttl`) modeling students, skills, criteria, companies, and drives.
  - Protégé-compatible with 4 SPARQL query examples (`ontology_queries.sparql`).

---

## 2. Project Architecture

```text
Campus Placement Prediction System/
│
├── app.py                      # Application factory and entry point
├── config.py                   # Centralized environment configuration
├── requirements.txt            # Pinned dependencies
├── README.md                   # Complete documentation
├── .gitignore                  # Git ignore rules
├── .env.example                # Sample environment variables
│
├── database/                   # SQLite persistence layer
│   ├── __init__.py
│   ├── db.py                   # Connection manager & foreign-key enforcement
│   ├── schema.sql              # Relational database schema with 15 tables
│   └── seed.py                 # Realistic sample demonstration seed script
│
├── models/                     # Domain entity representations
│   ├── __init__.py
│   ├── student.py              # Student model & profile completion logic
│   ├── company.py              # Company & JobRole models
│   ├── placement_drive.py      # PlacementDrive & Application models
│   ├── prediction.py           # Prediction assessment record model
│   └── recommendation.py       # Recommendation record model
│
├── routes/                     # Modular Flask Blueprints
│   ├── __init__.py
│   ├── auth_routes.py          # Register, login, logout
│   ├── dashboard_routes.py     # Admin & student dashboards
│   ├── student_routes.py       # Student profiles, academics, skills, projects
│   ├── company_routes.py       # Companies & job roles
│   ├── placement_routes.py     # Drives & applications
│   ├── prediction_routes.py    # Readiness evaluation endpoints
│   ├── recommendation_routes.py# Recommendations & skill gap API
│   └── report_routes.py        # Analytics & CSV export
│
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── student_service.py
│   ├── company_service.py
│   ├── placement_service.py
│   ├── prediction_service.py
│   ├── recommendation_service.py
│   └── report_service.py
│
├── prediction/                 # Machine learning pipeline
│   ├── __init__.py
│   ├── predictor.py            # Dual-mode inference engine (ML & Demo scoring)
│   ├── train_model.py          # Model training with real evaluation metrics
│   ├── preprocessing.py        # Feature extraction and encoding
│   ├── model_utils.py          # Joblib model persistence helpers
│   └── campus_placement_dataset.csv # Historical training dataset
│
├── ontology/                   # Semantic Knowledge Graph
│   ├── campus_placement_ontology.ttl # W3C Turtle RDF knowledge graph
│   ├── ontology_documentation.md     # Taxonomy & relationship specification
│   └── ontology_queries.sparql       # SPARQL queries
│
├── utils/                      # Helper decorators & validators
│   ├── __init__.py
│   ├── validators.py           # Input boundaries (CGPA 0-10, % 0-100, backlogs >= 0)
│   └── helpers.py              # Auth decorators, CSRF token generation/verification
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard/              # admin_dashboard.html, student_dashboard.html
│   ├── students/               # students.html, student_form.html, student_detail.html, edit_student.html
│   ├── companies/              # companies.html, company_form.html, company_detail.html
│   ├── placements/             # drives.html, drive_form.html, applications.html, placement_history.html
│   ├── predictions/            # prediction_form.html, prediction_result.html
│   ├── recommendations/        # recommendations.html
│   ├── reports/                # reports.html
│   └── errors/                 # 404.html, 500.html
│
├── static/                     # Assets
│   ├── css/                    # style.css, dashboard.css, forms.css, responsive.css
│   ├── js/                     # main.js, dashboard.js, charts.js, form_validation.js, predictions.js
│   └── images/                 # logo.svg
│
└── tests/                      # Automated test suite
    ├── __init__.py
    ├── test_database.py        # Foreign key & constraint tests
    ├── test_prediction.py      # Feature extraction & readiness logic tests
    └── test_routes.py          # Authentication, RBAC, and route tests
```

---

## 3. Technology Stack

- **Backend:** Python 3.10+ / 3.14, Flask 3.1+, Werkzeug 3.1+
- **Database:** SQLite 3 with enforced foreign keys (`PRAGMA foreign_keys = ON;`)
- **Machine Learning:** Scikit-learn (RandomForestClassifier, StandardScaler), Joblib, NumPy, Pandas
- **Knowledge Representation:** RDFLib, W3C RDF/Turtle, SPARQL 1.1
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Chart.js 4+, Font Awesome 6.5
- **Testing:** Pytest 8.3+

---

## 4. Windows Installation and Setup Guide

### Step 1: Clone or Navigate to the Workspace
Open PowerShell or Command Prompt in the project folder:
```powershell
cd "c:\Users\SND\Desktop\Campus Placement Prediction System"
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv venv
```

> [!TIP]
> If PowerShell displays `File ... Activate.ps1 cannot be loaded because running scripts is disabled on this system`, run this one-line command to permit scripts for the current terminal session:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\venv\Scripts\activate
> ```
> Or run Python directly through the virtual environment without activation:
> ```powershell
> .\venv\Scripts\python.exe app.py
> ```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
Default parameters in `.env`:
- `SECRET_KEY`: Session cryptographic signature key.
- `DATABASE_PATH`: `database/placement_system.db`
- `ADMIN_EMAIL`: `admin@campus.edu`
- `ADMIN_PASSWORD`: `AdminSecurePass@2026`

### Step 5: Initialize and Seed the Database
Initialize tables and realistic demonstration records:
```powershell
python database/seed.py
```

### Step 6: Train the Machine Learning Model (Optional / Ready Out-of-the-Box)
Train the Random Forest model on historical student records:
```powershell
python prediction/train_model.py
```
This generates and trains on `prediction/campus_placement_dataset.csv`, displaying real evaluation metrics (Accuracy, Precision, Recall, F1, Confusion Matrix), and persists `trained_model.joblib` and `preprocessor.joblib`.

### Step 7: Launch the Web Application
```powershell
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 5. Demonstration Accounts

| Role | Email Address | Password | Permissions |
|---|---|---|---|
| **Administrator** | `admin@campus.edu` | `AdminSecurePass@2026` | Full institutional access: manage students, companies, drives, review analytics, export CSVs. |
| **Student 1** | `priya.sharma@campus.edu` | `StudentPass@2026` | High readiness (CGPA 8.85, 0 backlogs, 1 internship, strong skills). |
| **Student 2** | `rahul.verma@campus.edu` | `StudentPass@2026` | Moderate readiness (CGPA 7.30, 0 backlogs, projects). |
| **Student 3** | `ananya.patel@campus.edu` | `StudentPass@2026` | Needs improvement (CGPA 6.20, 2 backlogs, gaps). |

---

## 6. Machine Learning Model Training Specification

### Input Feature Columns:
1. `tenth_percentage` (Float: 0.0 - 100.0)
2. `twelfth_percentage` (Float: 0.0 - 100.0)
3. `cgpa` (Float: 0.0 - 10.0)
4. `backlogs` (Integer: >= 0)
5. `attendance_percentage` (Float: 0.0 - 100.0)
6. `communication_score` (Integer: 1=Beginner, 2=Intermediate, 3=Advanced)
7. `aptitude_score` (Integer: 1=Beginner, 2=Intermediate, 3=Advanced)
8. `internship_count` (Integer: Count of verified internships)
9. `project_count` (Integer: Count of technical projects)
10. `certification_count` (Integer: Count of verified certifications)
11. `skill_count` (Integer: Count of technical skills)

### Target Column:
- `placement_status` (Binary: `1` = Placed / Ready, `0` = Not Placed / High Risk)

### Training a Custom Dataset:
```powershell
python prediction/train_model.py --csv path\to\your_custom_data.csv
```

---

## 7. RDF Ontology & Protégé Usage

The ontology file is located at `ontology/campus_placement_ontology.ttl`.

### Opening in Stanford Protégé:
1. Launch Protégé.
2. Select **File > Open...** and browse to `ontology/campus_placement_ontology.ttl`.
3. View the taxonomy under **Classes** (`Person` -> `Student`, `Skill` -> `TechnicalSkill` -> `ProgrammingSkill`, `Company`, `JobRole`, etc.).
4. Inspect relationships under **Object Properties** and **Data Properties**.
5. Switch to the **SPARQL Query** tab and run queries from `ontology/ontology_queries.sparql`.

---

## 8. Automated Testing

Run the test suite using pytest:
```powershell
pytest -v
```
All tests execute using isolated temporary databases without modifying development data.
