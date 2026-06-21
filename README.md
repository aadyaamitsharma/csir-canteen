# 🏛️ CSIR-CRRI Guest House & Canteen Indent Management System

A full-stack web application for managing canteen and guest house service indent requests through a multi-stage approval workflow.

---

## 📁 Folder Structure

```
csir_canteen/
├── app/
│   ├── __init__.py                  # Flask app factory
│   ├── models/
│   │   └── __init__.py              # All database models
│   ├── routes/
│   │   ├── auth.py                  # Login, logout, profile
│   │   ├── indentor.py              # Indentor dashboard & forms
│   │   ├── hod.py                   # HOD dashboard & approval
│   │   ├── chairman.py              # Chairman dashboard & approval
│   │   ├── manager.py               # Manager dashboard & status
│   │   ├── admin.py                 # Admin CRUD & analytics
│   │   └── api.py                   # REST API endpoints
│   ├── templates/
│   │   ├── shared/
│   │   │   └── base.html            # Base layout with sidebar
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── profile.html
│   │   ├── indentor/
│   │   │   ├── dashboard.html
│   │   │   ├── create_indent.html   # CSIR-style order form
│   │   │   ├── view_request.html
│   │   │   └── rate_service.html
│   │   ├── hod/
│   │   │   ├── dashboard.html
│   │   │   └── review_request.html
│   │   ├── chairman/
│   │   │   ├── dashboard.html
│   │   │   └── review_request.html
│   │   ├── manager/
│   │   │   ├── dashboard.html
│   │   │   └── manage_request.html
│   │   └── admin/
│   │       ├── dashboard.html
│   │       ├── users.html
│   │       ├── departments.html
│   │       ├── reports.html
│   │       └── analytics.html
│   └── static/
│       └── css/
│           └── main.css             # Full custom stylesheet
├── config.py                        # App configuration
├── run.py                           # Entry point
├── seed_db.py                       # Database seeder with dummy data
├── requirements.txt
└── README.md
```

---

## 🗄️ Database Schema

### Tables

| Table             | Key Columns |
|-------------------|-------------|
| `users`           | id, name, email, employee_id, password_hash, role, department_id |
| `departments`     | id, name, code |
| `indent_requests` | id, indent_number, indentor_id, department_id, event_type, venue, event_date, status, services... |
| `approval_logs`   | id, indent_id, approver_id, role, action, remarks, timestamp |
| `ratings`         | id, indent_id, rater_id, food_quality, service_quality, timeliness, overall, feedback |

### Workflow States
```
[Indentor Submits] → pending_hod
      ↓
  HOD Reviews
      ├── Reject → hod_rejected
      └── Approve → hod_approved
            ↓
      Chairman Reviews
            ├── Reject → chairman_rejected
            └── Approve → chairman_approved
                  ↓
            Manager Updates
                  ├── in_progress
                  └── completed → [Indentor Rates]
```

---

## ⚙️ Step-by-Step Setup Instructions

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- VS Code (recommended)
- Git (optional)

---

### Step 1 — Clone / Extract the Project

Place the `csir_canteen` folder somewhere on your system, e.g.:
```
C:\Users\YourName\Projects\csir_canteen\
```

---

### Step 2 — Create a Virtual Environment

Open **VS Code Terminal** (`Ctrl + ~`) and run:

```bash
cd csir_canteen
python -m venv venv
```

Activate it:
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

You should see `(venv)` in your terminal prompt.

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4 — Set Up MySQL Database

Open **MySQL Workbench** or **MySQL CLI** and run:

```sql
CREATE DATABASE csir_canteen CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

### Step 5 — Configure Database Connection

Open `config.py` and update your MySQL credentials:

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:YOUR_PASSWORD@localhost/csir_canteen'
```

Replace `YOUR_PASSWORD` with your MySQL root password.

---

### Step 6 — Seed the Database

This creates all tables AND loads sample data:

```bash
python seed_db.py
```

You should see:
```
✓ 6 departments created
✓ 8 users created
✓ 6 indent requests with approval logs and ratings created
DATABASE SEEDED SUCCESSFULLY!
```

---

### Step 7 — Run the Application

```bash
python run.py
```

Open your browser and go to: **http://localhost:5000**

---

## 🔑 Login Credentials

All accounts use password: **`csir@1234`**

| Role      | Email                  |
|-----------|------------------------|
| Admin     | admin@csir.in          |
| HOD       | hod@csir.in            |
| Chairman  | chairman@csir.in       |
| Manager   | manager@csir.in        |
| Indentor  | indentor@csir.in       |
| Indentor  | anita@csir.in          |
| Indentor  | vikram@csir.in         |

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications` | Get pending notification count |
| GET | `/api/requests/status/<id>` | Get request status |
| GET | `/api/users/search?q=` | Search users (admin only) |
| GET | `/admin/analytics/data` | Chart data as JSON |

---

## ✨ Features

- **Multi-stage approval**: Indentor → HOD → Chairman → Manager
- **CSIR-style indent form** matching the official canteen order format
- **Role-based dashboards** with stats and tables
- **Approval timeline** with remarks at each stage
- **Service rating system** (food, service, timeliness, overall)
- **Admin panel**: Create/edit/delete users and departments
- **Analytics charts**: Department-wise, status, monthly trend, ratings
- **Search & filter** in reports
- **Responsive design** with sidebar navigation
- **Notification badge** for pending actions
- **Session-based authentication** with Flask-Login

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Bootstrap 5, Chart.js |
| Backend | Python 3, Flask |
| ORM | Flask-SQLAlchemy |
| Database | MySQL 8 |
| Auth | Flask-Login + Flask-Bcrypt |
| Fonts | Google Fonts (DM Sans + Playfair Display) |

---

## 🔧 Common Issues

**`ModuleNotFoundError`** → Make sure virtual env is activated: `venv\Scripts\activate`

**MySQL connection error** → Check your password in `config.py`

**`Access denied`** error on login → Run `seed_db.py` first to create users

**Port already in use** → Change port in `run.py`: `app.run(debug=True, port=5001)`

---

## 📜 License

Built for CSIR-CRRI internal use. For academic/college project demonstration.
