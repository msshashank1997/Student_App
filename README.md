# Student Management System (Flask + Pytest + Jenkins + Docker)

A web application for managing student records using Flask and MongoDB.

## 📌 Features
- Add, view, fetch, and delete students
- REST API with Flask
- Tested with pytest
- Dockerized
- CI/CD ready with Jenkins
- Email notifications via SMTP

## 🚀 Run Locally
```bash
pip install -r requirements.txt
python app.py
```

## 🧪 Run Tests
```bash
pytest test_app.py
```

## 🐳 Docker
```bash
docker build -t student-api .
docker run -p 5000:5000 student-api
```

## 🛠️ Jenkins Pipeline
This project contains a `Jenkinsfile` to automate:
- Code clone
- Dependency install
- Test execution
- Docker image build and push
- App deployment
- SMTP email notifications for build status

## Generate App passwords

- Navigate to https://myaccount.google.com/apppasswords
- Sign in to your Google Account
- Select the app (Mail) and device (Other - custom name)
- Enter a name for the app password (e.g., "Student App SMTP")
- Click "Generate"
- Use the generated 16-character password in your application's SMTP configuration
- Note: App passwords are only available if you have 2-Step Verification enabled for your Google account

## 📧 SMTP Configuration
The application supports email notifications for various events:
- Configure SMTP settings in the environment variables
- Emails are sent for student registration and account activities
- Build status notifications from Jenkins pipeline

## API Endpoints

- `GET` `/api/students` - Get all students
- `POST` `/api/students` - Add a new student
- `GET` `/api/students/<student_id>` - Get student by ID
- `DELETE` `/api/students/<student_id>` - Delete student
- `GET` `/api/students/name/<name>` - Search students by name

## Web Pages

- `/` - Home page
- `/web/students` - View all students
- `/web/add_student` - Add a new student