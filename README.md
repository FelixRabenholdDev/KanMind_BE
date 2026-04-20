# 📌 Board & Task Management API (Django REST Framework)

A backend API for managing boards, tasks, and collaborative workflows.
Built with Django and Django REST Framework, supporting authentication, board membership, task assignment, and comment tracking.

---

## 🚀 Features

- 🔐 Email-based authentication with token login
- 📋 Board management (create, update, delete, member handling)
- ✅ Task management with status & priority workflow
- 👥 Board membership system (owners + members)
- 💬 Task comments system
- 🔎 Filtered task views (assigned to me / reviewing)
- 📊 Board statistics (member count, task counts, priority metrics)
- 🛡️ Role-based permissions (owner, member, superuser)

---

## 🏗️ Tech Stack

- Python 3.12+
- Django 6.0.4
- Django REST Framework 3.17.1
- django-cors-headers 4.9.0
- python-dotenv 1.2.2
- SQLite (default, configurable)

---

## 📦 Installation

### 1. Clone repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

---

### 2. Create virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment Variables

Create a .env file in the root directory:

```env
SECRET_KEY=your-secret-key
DEBUG=True
```

---

## 🗄️ Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

Create a superuser:

```bash
python manage.py createsuperuser
```

---

## ▶️ Run Server

```bash
python manage.py runserver
```

Server runs at:

http://127.0.0.1:8000/

---

## 🔐 Authentication

The API uses Token Authentication.

### Login
POST /api/login/

### Register
POST /api/registration/

### Email Check
GET /api/email-check/?email=test@example.com

### Authorization Header

Authorization: Token <your_token>

---

## 📌 API Overview

### 🧑 Authentication
- POST /api/login/
- POST /api/registration/
- GET /api/email-check/

---

### 📋 Boards
- GET /api/boards/
- POST /api/boards/
- GET /api/boards/{id}/
- PATCH /api/boards/{id}/
- DELETE /api/boards/{id}/

---

### ✅ Tasks
- POST /api/tasks/
- GET /api/tasks/{id}/
- PATCH /api/tasks/{id}/
- DELETE /api/tasks/{id}/

Filtered:
- GET /api/tasks/assigned-to-me/
- GET /api/tasks/reviewing/

---

### 💬 Comments
- GET /api/tasks/{id}/comments/
- POST /api/tasks/{id}/comments/
- DELETE /api/tasks/{id}/comments/{comment_id}/

---

## 🛡️ Permissions

- Superuser → full access
- Board owner → full control over boards & tasks
- Board members → access to assigned boards/tasks
- Comment author → can delete own comments

---

## 📁 Project Structure

auth_app/
boards_app/
    api/
        views.py
        serializers.py
        permissions.py
        boards_urls.py
        tasks_urls.py
manage.py
requirements.txt

---

## 🧠 Notes

- Custom user model with email authentication
- Boards use many-to-many membership via intermediate model
- Tasks support status + priority workflow
- Filtering is path-based (assigned / reviewing)
- Designed for frontend integration (React/Vue/Angular)

---

## 📄 License

MIT License

---

## 👨‍💻 Author

Backend project built with Django REST Framework for learning and portfolio purposes.
