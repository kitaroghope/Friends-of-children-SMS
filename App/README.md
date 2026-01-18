# Friends of Children School Management System (SMS)

A comprehensive, multi-school school management system built with Django 6.0.1 and PostgreSQL. Designed for schools in East Africa with support for offline data entry, role-based access control, and complete audit trails.

---

## What This System Does

The Friends of Children SMS is a full-featured school management platform that handles:

### Core Operations
- **School Management**: Register and manage multiple schools with custom configurations (currency, grading systems, promotion rules)
- **Academic Structure**: Define academic years, terms, sections (Pre-Primary/Primary), classes, and subjects
- **Student Management**: Enroll students, track their status (Active, Completed, Transferred, Dropped), and maintain enrollment history
- **Staff Management**: Manage teachers and administrative staff with status tracking (Active, Suspended, On Leave, Terminated)
- **Parent Management**: Link multiple parents/guardians to students with emergency contact support

### Assessments & Results
- **Exam Management**: Create exam sets, define exams per subject, and record student results
- **Grading Systems**: Configurable grade scales (D1-D9 for Primary, A-F for Pre-Primary)
- **Result History**: Immutable audit trail of all result changes

### Student Progression
- **Promotion Rules**: Configurable policies per class (last exam only, selected exam sets, with compulsory subjects)
- **Automatic & Manual Promotion**: Bulk promotion with override capabilities
- **Promotion Audit Trail**: Complete history of promotion decisions

### Financial Management
- **Fee Structures**: Define fees per class/term
- **Student Fees**: Apply discounts with reasons
- **Invoices**: Generate and manage invoices per parent
- **Payments**: Record payments and allocate to invoices
- **Credits & Refunds**: Handle overpayments and process refunds

### Access Control
- **Role-Based Permissions**: Granular permissions for Academic, Finance, and Admin functions
- **Staff Roles**: Assign multiple roles per staff member with expiration dates
- **Permission Categories**: academic.create_exam, finance.approve_refund, admin.manage_roles, etc.

### Offline Capability
- **Sync Queue**: Queue offline data entries for synchronization
- **Conflict Resolution**: Flag and resolve data conflicts
- **Validation**: Server-side validation of offline entries

### Reporting
- **Academic Reports**: Termly progress cards, class performance summaries
- **Financial Reports**: Parent statements, payment histories
- **Audit Reports**: Complete audit trail exports

---

## Prerequisites

- Python 3.10+
- PostgreSQL 13+
- pip (Python package manager)

---

## Setup Instructions

### 1. Clone and Navigate
```bash
cd C:\xampp\htdocs\kiiza-repo\Friends-of-children-SMS\App
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install django>=6.0.1 djangorestframework django-cors-headers
pip install psycopg[binary] django-filter python-dateutil
pip install Pillow  # For image fields
```

### 4. Configure Database

Create a PostgreSQL database:
```sql
CREATE DATABASE school_sms;
```

Update `App/settings.py` with your database credentials (default password is `kitahope`):
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'school_sms',
        'USER': 'postgres',
        'PASSWORD': 'kitahope',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
# Email: admin@school.com
# Password: kitahope
```

### 7. Start the Server
```bash
python manage.py runserver
```

### 8. Access the Application

- **Home Page**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API Endpoints**: http://localhost:8000/api/

---

## API Endpoints

### Authentication
```
POST /api/accounts/token/          - Get JWT token
POST /api/accounts/token/refresh/  - Refresh token
POST /api/accounts/register/       - Register user (public)
```

### School Registration
```
POST /api/accounts/school-requests/              - Submit school request (public)
GET  /api/accounts/school-requests/              - List requests (superadmin)
PUT  /api/accounts/school-requests/<id>/         - Approve/reject request
POST /api/accounts/onboarding/school/            - Create school from request
```

### Staff & Parent Onboarding
```
POST /api/accounts/onboarding/staff/   - Add staff member
POST /api/accounts/onboarding/parent/  - Add parent
```

### School Setup
```
GET  /api/accounts/setup/  - Check setup status
POST /api/accounts/setup/  - Initialize school structure
```

### Public Registration Pages
```
GET /register/school/  - School registration form
GET /register/         - User registration form
GET /onboard/staff/    - Add staff members (requires JWT)
GET /onboard/parent/   - Add parents (requires JWT)
```

---

## Complete Onboarding Flow

### Step 1: Submit School Request (Public)
1. Go to http://localhost:8000/register/school/
2. Fill in requester and school information
3. Submit for review

### Step 2: Review Request (Superadmin)
1. Superadmin logs into Django admin at http://localhost:8000/admin/
2. Navigate to Core > School requests
3. Select pending requests
4. Choose "Approve selected requests" or "Reject selected requests" from actions dropdown

### Step 3: Create School from Request (Superadmin)
```bash
# Get JWT token
curl -X POST http://localhost:8000/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@school.com", "password": "kitahope"}'

# Create school from approved request
curl -X POST http://localhost:8000/api/accounts/onboarding/school/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"request_id": 1}'
```

### Step 4: Initial School Setup (School Owner)
1. School owner gets JWT token at `/api/accounts/token/`
2. Call `POST /api/accounts/setup/` or use http://localhost:8000/onboard/staff/
3. This creates:
   - Academic Year (current year)
   - 3 Terms
   - Pre-Primary & Primary Sections
   - Default Grade Scale (D1-D9)

### Step 5: Add Staff Members (School Admin)
1. Go to http://localhost:8000/onboard/staff/
2. Enter your JWT token
3. Fill in staff details (email, password, name, staff number, department, position)
4. Submit to create staff account

### Step 6: Add Parents (School Staff)
1. Go to http://localhost:8000/onboard/parent/
2. Enter your JWT token
3. Fill in parent details
4. Submit to create parent record

---

## User Roles

1. **Super Admin**: Platform-level administration (via Django admin)
2. **School Administrator**: Full access to their school's data
3. **Teacher**: Can enter marks, view results
4. **Finance Officer**: Manage fees, invoices, payments
5. **Parent**: View their children's progress and financial statements

---

## Technology Stack

- **Backend**: Django 6.0.1
- **API**: Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (Simple JWT)
- **Frontend**: Carbon Design System (pure CSS, no jQuery/Bootstrap)
- **CORS**: django-cors-headers

---

## Project Structure

```
App/
├── manage.py
├── App/
│   ├── settings.py
│   └── urls.py
├── core/           # Base models, School, AuditLog, Config
├── schools/        # AcademicYear, Term, Section
├── accounts/       # Custom User, authentication
├── academic/       # Class, Subject, TeachingAssignment
├── students/       # Student, Enrollment
├── staff/          # StaffProfile
├── parents/        # ParentProfile
├── permissions/    # Role, Permission, StaffRole
├── exams/          # ExamSet, Exam, Result, GradeScale
├── promotion/      # PromotionRule, PromotionRecord
├── finance/        # FeeStructure, Invoice, Payment, Refund
├── offline/        # SyncQueue, Conflict resolution
├── reports/        # Report generation
└── templates/      # HTML pages with Carbon design
```

---

## Key Features

- **Multi-School Ready**: All models reference a school for data isolation
- **Offline First**: Queue offline data for synchronization
- **Full Audit Trail**: Track all changes to critical data
- **Policy-Driven**: Configurable promotion rules, grading scales, finance settings
- **Historical Data**: Status changes preserved, no data overwrites
- **Role-Based**: Granular permissions per school

---

## License

This project is proprietary software.

---

## Support

For support, contact: support@friendsofchildren.edu

---

**Made with love by kitaroghope**
