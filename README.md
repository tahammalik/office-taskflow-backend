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

### Multi-Tenancy & Security Architecture

Office TaskFlow is built with an enterprise-grade focus on security and data isolation, moving beyond simple single-tenant architectures:

- **Logical Tenant Isolation:** Every data entity (`User`, `Team`, `Project`, `Task`) is explicitly bounded to an `organization_id`. Database query execution paths enforce this boundary to ensure a tenant can never access another company's data workspace.
- **IDOR Protection Matrix:** The API actively defends against Insecure Direct Object Reference (IDOR) attacks. Custom FastAPI dependency injections inspect the incoming user's tenant context from their validated token before executing relational database table joins.
- **Cryptographic Core:** Implements enterprise-grade `Argon2` password hashing with custom peppering logic for high resistance to GPU-accelerated brute-force attacks.
- **Data Lifecycle Safeguards:** Implements a soft-deletion framework using an `is_deleted` column flag. Progress monitoring and analytics queries filter out archived corporate structures to protect system metrics and maintain data integrity.

### Database Schema & Relationship Matrix

The system relies on a clean relational architecture handled via SQLAlchemy ORM with cascade constraints to maintain referential integrity:

- **Organizations ──> Users:** (One-to-Many) An organization contains multiple employees; users hold an optional `organization_id` for independent or corporate tracking.
- **Organizations ──> Teams:** (One-to-Many) Workspace structures are grouped into distinct teams bounded by the organization tenant flag.
- **Organizations ──> Projects:** (One-to-Many) High-level operations managed directly at the company workspace layer.
- **Teams <──> Projects:** (Many-to-Many via `project_teams` junction table) Multiple teams can collaborate on multiple projects. The junction table utilizes a composite primary key (`project_id`, `team_id`) for link mapping.
- **Teams ──> Tasks:** (One-to-Many) Tasks are dispatched within the scope of a team and assigned to explicit team members.
