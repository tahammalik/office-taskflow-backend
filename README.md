# 🚀 Project Management & Authentication API

> **A production-ready FastAPI backend for team collaboration, project tracking, and secure authentication**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.135.3-green.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-2.0-blue.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Role-Based Access Control](#role-based-access-control)
- [Configuration](#configuration)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This is a comprehensive **Project Management & Authentication API** built with FastAPI, designed to handle multi-organization workflows with role-based access control. The system supports user authentication, organization management, team collaboration, project tracking, and task assignment.

### Key Capabilities

- 🔐 **Secure Authentication** - JWT-based auth with Argon2 password hashing
- 🏢 **Multi-Organization Support** - Create and manage multiple organizations
- 👥 **Team Management** - Organize users into teams with specific roles
- 📊 **Project Tracking** - Create, assign, and monitor projects
- ✅ **Task Management** - Assign tasks and track progress
- 🔒 **Role-Based Access** - Admin, Manager, and Employee role hierarchy

---

## ✨ Features

### Authentication & Security
- ✅ **JWT Token Authentication** - Secure access tokens with configurable expiry (30 minutes default)
- ✅ **Argon2 Password Hashing** - Industry-leading password security with peppering
- ✅ **OAuth2 Password Flow** - Standard OAuth2 implementation for token generation
- ✅ **Custom Exception Handlers** - Graceful error handling for UserNotFound, EmailExists, etc.

### Organization Management
- ✅ **Create Organizations** - Users can create their own organizations
- ✅ **Delete Organizations** - Admin-only organization deletion with cleanup
- ✅ **Auto-Assign Admin Role** - Creator becomes admin of the organization

### Team & Group Management
- ✅ **Create Teams** - Manager/Admin can create teams with descriptions
- ✅ **Delete Teams** - Remove teams from the system
- ✅ **Role Restrictions** - Only managers and admins can manage teams

### Project Management
- ✅ **Create Projects** - Define projects with title, description, and deadlines
- ✅ **View Projects** - List all projects within an organization
- ✅ **Auto-Link Organization** - Projects automatically linked to creator's organization
- ✅ **Role-Based Access** - Only admins and managers can create/view projects

### Task Management
- ✅ **Create Tasks** - Assign tasks to team members
- ✅ **View My Tasks** - Employees can view their assigned tasks
- ✅ **Track Progress** - Managers/Admins can view all tasks and progress
- ✅ **Role-Based Visibility** - Different views based on user role

### Database & Performance
- ✅ **PostgreSQL Database** - Robust relational database with SQLAlchemy ORM
- ✅ **Connection Pooling** - Efficient database connection management
- ✅ **Alembic Migrations** - Schema version control and migrations
- ✅ **CORS Support** - Configured for cross-origin requests

### Developer Experience
- ✅ **Auto-Generated Docs** - Swagger UI at `/docs` and ReDoc at `/redoc`
- ✅ **Pydantic Validation** - Request/response validation with custom schemas
- ✅ **Structured Logging** - Comprehensive logging for debugging and monitoring
- ✅ **Dependency Injection** - Clean architecture using FastAPI's DI system

---

## 🛠️ Tech Stack

| Category | Technology | Version |
|----------|-----------|---------|
| **Framework** | FastAPI | 0.135.3 |
| **Server** | Uvicorn (ASGI) | 0.44.0 |
| **ORM** | SQLAlchemy | 2.0.49 |
| **Database** | PostgreSQL | psycopg2-binary 2.9.11 |
| **Migrations** | Alembic | 1.18.4 |
| **Authentication** | PyJWT | 2.12.1 |
| **Password Hashing** | Argon2-cffi | 25.1.0 |
| **Validation** | Pydantic | Latest |
| **Config Management** | Pydantic-settings | 2.13.1 |
| **Caching** | Redis | 7.4.0 *(optional)* |

---

## 🏗️ Architecture

```
app/
├── api/v1/                      # API Routes (Version 1)
│   ├── user_auth.py            # User registration, login, token endpoints
│   ├── organization_auth.py    # Organization CRUD operations
│   ├── teams.py                # Team/Group management
│   ├── projects.py             # Project creation and listing
│   └── tasks.py                # Task management and progress tracking
│
├── core/                        # Core Configuration & Utilities
│   ├── config.py               # Environment & secret configuration
│   ├── db.py                   # Database connection setup
│   ├── dependencies.py         # FastAPI dependencies (auth, roles)
│   ├── exceptions.py           # Custom exception classes
│   ├── redis_client.py         # Redis client (optional caching)
│   └── security.py             # Password hashing, JWT token creation
│
├── models/                      # SQLAlchemy Database Models
│   ├── user_model.py           # User table schema
│   ├── organization_model.py   # Organization table schema
│   ├── team_model.py           # Team table schema
│   ├── project_model.py        # Project table schema
│   └── task_model.py           # Task table schema
│
├── schemas/                     # Pydantic Schemas for Validation
│   ├── user_schema.py          # User request/response schemas
│   ├── token_schema.py         # JWT token schemas
│   ├── organization_schema.py  # Organization schemas
│   ├── team_schema.py          # Team schemas
│   ├── project_schema.py       # Project schemas
│   └── task_schema.py          # Task schemas
│
├── services/                    # Business Logic Layer
│   ├── user_service.py         # User authentication & queries
│   ├── organization_service.py # Organization business logic
│   ├── team_service.py         # Team operations
│   └── task_service.py         # Task creation & management
│
└── main.py                      # Application entry point
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+
- Redis 7+ (optional, for future caching features)
- pip or poetry for dependency management

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/project-management-api.git
cd project-management-api
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

Create `.env` file for database configuration:

```env
# .env
DRIVERNAME=postgresql
USERNAME=your_db_username
PASSWORD=your_db_password
HOST=localhost
PORT=5432
DATABASE=project_management_db
```

Create `.key` file for security secrets:

```env
# .key
PASSWORD_SECRET_KEY=your_pepper_secret_key_here
DUMMY_HASH=$argon2id$v=19$m=65536,t=3,p=4$example$hash
SECRET_KEY=your_jwt_secret_key_minimum_32_chars_long
ALGORITHM=HS256
```

> ⚠️ **Security Note**: Never commit `.env` or `.key` files to version control. These files contain sensitive credentials.

#### 6. Start the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

```

#### 7. Access the API

- **Base URL**: `http://localhost:8000`
- **Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/home`

---

## 📡 API Endpoints

### Authentication (`/auth/v1`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/v1/user/create` | Register new user | ❌ |
| POST | `/auth/v1/token` | Login & get JWT token | ❌ |
| GET | `/auth/v1/me` | Get current user info | ✅ |

### Organization (`/org/login`)

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| POST | `/org/login/` | Create new organization | ✅ | Any |
| DELETE | `/org/login/delete/{org_id}` | Delete organization | ✅ | Admin |

### Teams (`/groups/v1`)

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| POST | `/groups/v1/create_group` | Create new team | ✅ | Manager, Admin |
| DELETE | `/groups/v1/delete/team/{id}` | Delete team | ✅ | Manager, Admin |

### Projects (`/projects/v1`)

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| POST | `/projects/v1/create` | Create new project | ✅ | Manager, Admin |
| GET | `/projects/v1/show/` | List all projects | ✅ | Manager, Admin |

### Tasks (`/task/v1`)

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| POST | `/task/v1/` | Create new task | ✅ | Manager, Admin |
| GET | `/task/v1/my_tasks` | View assigned tasks | ✅ | Any |
| GET | `/task/v1/progress` | View task progress | ✅ | Manager, Admin |

---

## 🔐 Role-Based Access Control

The API implements a three-tier role system:

### Roles Hierarchy

```
┌─────────────┐
│    Admin    │  ← Full access to all features
├─────────────┤
│   Manager   │  ← Can create projects, tasks, teams
├─────────────┤
│   Employee  │  ← Can view assigned tasks only
└─────────────┘
```

### Permission Matrix

| Feature | Admin | Manager | Employee |
|---------|-------|---------|----------|
| Create User | ✅ | ❌ | ❌ |
| Create Organization | ✅ | ✅ | ✅ |
| Delete Organization | ✅ | ❌ | ❌ |
| Create Team | ✅ | ✅ | ❌ |
| Delete Team | ✅ | ✅ | ❌ |
| Create Project | ✅ | ✅ | ❌ |
| View Projects | ✅ | ✅ | ❌ |
| Create Task | ✅ | ✅ | ❌ |
| View My Tasks | ✅ | ✅ | ✅ |
| View All Tasks | ✅ | ✅ | ❌ |

---

## ⚙️ Configuration

### Environment Variables (.env)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DRIVERNAME` | Database driver | `postgresql` | ✅ |
| `USERNAME` | Database username | - | ✅ |
| `PASSWORD` | Database password | - | ✅ |
| `HOST` | Database host | `localhost` | ✅ |
| `PORT` | Database port | `5432` | ✅ |
| `DATABASE` | Database name | - | ✅ |

### Security Keys (.key)

| Variable | Description | Required |
|----------|-------------|----------|
| `PASSWORD_SECRET_KEY` | Pepper for password hashing | ✅ |
| `DUMMY_HASH` | Example Argon2 hash format | ✅ |
| `SECRET_KEY` | JWT signing key (min 32 chars) | ✅ |
| `ALGORITHM` | JWT algorithm | ✅ |

---

## 🧪 Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app
```

### Code Style

```bash
# Install linting tools
pip install black flake8 mypy

# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Docker Support (Optional)

```bash
# Build Docker image
docker build -t project-management-api .

# Run container
docker run -p 8000:8000 --env-file .env project-management-api
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Contribution Guidelines

- Follow PEP 8 style guidelines
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit
- [Argon2](https://github.com/hynek/argon2-cffi) - Secure password hashing
- [PyJWT](https://pyjwt.readthedocs.io/) - JSON Web Tokens

---

## 📞 Support

For support, please open an issue in the repository or contact me.

**Built with ❤️ using FastAPI**
