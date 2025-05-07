
# 🛠 Django REST API for Job Board Platform

This is the backend system for a Job Board Platform, built using **Django** and designed to expose a **REST API** for managing jobs, applications, tags, companies, and authentication. The architecture separates route handling, business logic, and data access concerns, and supports asynchronous operations using a queue system. It uses a **PostgreSQL** database for data persistence.

---

## 📐 Architecture Overview

Refer to the high level architecture diagram in [High level architecture file](./diagrams/high level arch.drawio)

> To view the diagram easily, make sure to install drawio extension in your editor.

---

## 🔧 Features

* 🧑‍💼  **User Authentication** : Secure login/signup and protected routes.
* 💼  **Job Management** : Create, read, update, delete job posts.
* 🏷  **Tags** : Categorize jobs with tags.
* 🏢  **Companies** : Associate jobs with companies.
* 📄  **Job Applications** : Users can apply to jobs.
* 📬  **Queue Integration** : For processing tasks asynchronously.
* 🗃  **Modular Structure** :
  * **Route Handlers** for REST APIs
  * **Business Logic** layer
  * **Data Access** layer for DB operations

---

## 🧱 Tech Stack

| Layer            | Technology                          |
| ---------------- | ----------------------------------- |
| Framework        | Django                              |
| API              | Django REST Framework               |
| Database         | PostgreSQL                          |
| Queue (optional) | Celery / Redis                      |
| ORM              | Django ORM                          |
| Authentication   | JWT or session-based (customizable) |

---

## 🚀 Getting Started

### 1. Clone the Repo

```bash
git clone <the link of the repo>
cd job-portal
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database

Update your `settings.py` or `.env` with PostgreSQL credentials:

```env
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_pass
DB_HOST=localhost
DB_PORT=5432
```

Then run migrations:

```bash
python manage.py migrate
```

### 5. Run the Server

```bash
python manage.py runserver
```

---

## 🧪 Running Tests

```bash
python manage.py test
```

---

## 📝 API Endpoints

| Resource     | Endpoint               | Method(s) |
| ------------ | ---------------------- | --------- |
| Auth         | `/api/auth/`         | POST, GET |
| Jobs         | `/api/jobs/`         | CRUD      |
| Applications | `/api/applications/` | CRUD      |
| Companies    | `/api/companies/`    | CRUD      |
| Tags         | `/api/tags/`         | CRUD      |

---

## 📥 Queue Integration (Optional)

If using Celery with Redis:

```bash
celery -A your_project_name worker --loglevel=info
```

---

## 🧭 Project Structure

```
job_board_backend/
├── jobs/
├── applications/
├── companies/
├── tags/
├── auth/
├── core/               # Shared utils, services
├── api/                # Route handlers
├── services/           # Business logic
├── repositories/       # Data access
├── manage.py
└── requirements.txt
```

---

## 📜 License

MIT License © Your Name
