# ✅ Smart Task Management System

A Python web application built with Flask, PostgreSQL, Pandas/NumPy, WebSockets, and HTML/CSS.

---

## 📁 Project Structure

```
smart_task_manager/
├── app.py              ← Main Flask app (routes, auth, REST APIs, WebSocket)
├── database.py         ← SQLAlchemy models (User, Task)
├── analytics.py        ← Pandas & NumPy analytics module
├── schema.sql          ← PostgreSQL database schema
├── requirements.txt    ← Python dependencies
├── .env.example        ← Environment variable template
├── .gitignore
├── templates/
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── static/
    ├── css/style.css
    └── js/app.js
```

---

## ⚙️ Setup Instructions (Step by Step)

### PHASE 1 — Install PostgreSQL

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### On macOS (Homebrew):
```bash
brew install postgresql
brew services start postgresql
```

#### On Windows:
Download installer from https://www.postgresql.org/download/windows/

---

### PHASE 2 — Create Database & User

```bash
# Open PostgreSQL shell
sudo -u postgres psql

# Run these commands inside psql:
CREATE DATABASE taskdb;
CREATE USER taskuser WITH PASSWORD 'taskpassword';
GRANT ALL PRIVILEGES ON DATABASE taskdb TO taskuser;
\q
```

**OR** run the schema file directly:
```bash
sudo -u postgres psql -f schema.sql
```

---

### PHASE 3 — Clone & Setup Python Environment

```bash
# Clone your repo (or navigate to project folder)
cd smart_task_manager

# Create virtual environment
python -m venv venv

# Activate it:
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

### PHASE 4 — Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your values:
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=postgresql://taskuser:taskpassword@localhost:5432/taskdb
```

To generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### PHASE 5 — Run the Application

```bash
# Make sure venv is activated
python app.py
```

You should see:
```
✅ Database tables created.
 * Running on http://0.0.0.0:5000
```

Open your browser: **http://localhost:5000**

---

## 🚀 Features

| Feature | Technology |
|---|---|
| User Registration & Login | Flask + Werkzeug |
| Session Management | Flask sessions |
| REST APIs (CRUD) | Flask routes |
| Database Storage | PostgreSQL + SQLAlchemy |
| Analytics | Pandas + NumPy |
| Real-time Updates | WebSockets (Flask-SocketIO) |
| Frontend UI | HTML + CSS (responsive) |

---

## 📡 REST API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/register` | Register new user |
| POST | `/api/login` | Login user |
| POST | `/api/logout` | Logout user |

### Tasks
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/tasks` | Get all tasks (auth required) |
| POST | `/api/tasks` | Add new task (auth required) |
| PUT | `/api/tasks/<id>` | Update task (auth required) |
| DELETE | `/api/tasks/<id>` | Delete task (auth required) |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/analytics` | Get task analytics (auth required) |

---

## 📦 Task Object Format

```json
{
  "id": 1,
  "title": "Complete assignment",
  "description": "Finish the Flask project",
  "priority": "high",
  "status": "in_progress",
  "created_at": "2024-01-15 10:30:00",
  "user_id": 1
}
```

**Priority values:** `low` | `medium` | `high`  
**Status values:** `pending` | `in_progress` | `completed`

---

## 🔌 WebSocket Events

| Event | Direction | Description |
|---|---|---|
| `connect` | Server → Client | On connection established |
| `task_added` | Server → Client | Broadcast when task is added |
| `task_updated` | Server → Client | Broadcast when task is updated |
| `task_deleted` | Server → Client | Broadcast when task is deleted |

---

## 📊 Analytics (Pandas & NumPy)

The `/api/analytics` endpoint returns:
- Total tasks count
- Completed / Pending / In-Progress counts
- Completion percentage (NumPy calculation)
- Priority breakdown (low / medium / high)
- Average tasks created per day

---

## 🗃️ Database Schema

### `users` table
| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | Auto increment |
| username | VARCHAR(80) | Unique |
| email | VARCHAR(120) | Unique |
| password_hash | VARCHAR(256) | Werkzeug hashed |
| created_at | TIMESTAMP | Auto set |

### `tasks` table
| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | Auto increment |
| title | VARCHAR(200) | Required |
| description | TEXT | Optional |
| priority | VARCHAR(20) | low/medium/high |
| status | VARCHAR(30) | pending/in_progress/completed |
| created_at | TIMESTAMP | Auto set |
| user_id | INTEGER FK | References users(id) |
