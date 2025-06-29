# School_Management_System
# 🎓 School Management System (Django-Based)

A powerful and user-friendly **School Management System** built with Django, designed to simplify and streamline the administration of schools. This system supports multiple user roles and comes with dynamic dashboards, report cards, fee tracking, exam scheduling, and more.

---

## 🚀 Features

### 🔐 Role-Based Logins
- **Principal**
- **Headmaster**
- **Teachers**
- **Students**
- **Accountants**

### 📊 Student Dashboard
- Attendance summary with charts
- Exam marks by subject and exam type
- Report card PDF download
- Leave application
- Fee payment and history
- Upcoming exams and holidays

### 👨‍🏫 Teacher Dashboard
- Add students and assign marks
- Record daily attendance
- Approve leave requests
- View monthly salary slips
- View assigned students

### 👨‍💼 Headmaster Panel
- Approve/reject teachers and students
- Manage exam schedules (create, edit, delete)
- View and manage teacher/student data

### 📋 Admin Features
- Superuser access to all modules via Django Admin Panel
- Holiday and Event Management
- Calendar integration using FullCalendar.js
- Secure password reset functionality for all roles

---

## 🧑‍💻 Tech Stack

- **Backend:** Django 5.x
- **Frontend:** HTML, CSS, JavaScript, Chart.js, FullCalendar.js
- **Database:** SQLite (default, can be switched to PostgreSQL)
- **PDF Generation:** WeasyPrint (for report cards)
- **Authentication:** Django’s built-in authentication with role-based control

---

## 📸 Screenshots

| Dashboard Examples | |
|--------------------|--|


---

## 📂 Project Structure

```bash
sms/
├── accounts/         # Handles authentication and custom user model
├── students/         # Student-specific views and dashboard
├── teachers/         # Teacher views and tools
├── headmaster/       # Headmaster controls (exam scheduling, approval)
├── principal/        # Principal views and data analytics
├── accountant/       # Fee tracking and history
├── templates/        # Role-based and shared HTML templates
├── static/           # CSS, JS, images, FullCalendar, etc.
├── media/            # Uploaded files like payslips, PDFs
├── manage.py

```

##🔧 Setup Instructions

Clone the repository
```bash
git clone https://github.com/yourusername/school-management-system.git
cd school-management-system
```

Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

Install dependencies
```bash
pip install -r requirements.txt
```

Apply migrations
```bash
python manage.py migrate
```

Create a superuser
```bash
python manage.py createsuperuser
```

Run the development server
```bash
python manage.py runserver
```
