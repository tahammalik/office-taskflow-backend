# Office TaskFlow — Backend
> A B2B backend API for managing organizations.projects,teams and tasks - built with FastAPI,Postgresql and Redis
## What is This?
Office Taskflow is a multi-tenant task management system build for businesses.Each organization gets its own workspace where admin can create team assign project and track employee tasks across projects.

Think of it like a lightweight Jira or Asana — but built from scratch to learn real-world backend engineering.

### Key Features
- **Authentication** - JWT Authentication with Argon2 password hashing.
- **Account lockout** -  brute-force protection via Redis (locks after 5 failed attempts).
- **Organization Management** - create and manage your company workspace.
- **Team Management** - group employees into teams with a designated leader.
- **Project Management** - create projects and assign them to teams.
- **Task Management** - assign tasks to employees with deadlines and status tracking.
- **Role-Based Access Control** - admin, manager, employee roles with enforced permissions.
- **Structured Logging** — request and error logging throughout the app.
