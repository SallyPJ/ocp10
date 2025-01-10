# Softdesk Project

## Overview
Softdesk is a bug tracking and project management tool built with Django and Django REST Framework.  
It allows users to create and manage projects and report issues.
## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Endpoints](#endpoints)
  - [Users](#users)
  - [Projects](#projects)
  - [Issues](#issues)
  - [Comments](#comments)
- [Permissions](#permissions)
- [License](#license)


## Features
- **Authentication**: Secured using JSON Web Tokens (JWT).
- **Permissions**: Granular control over user actions (Admin, Project Manager, Contributor).
- **Project Management**: CRUD operations for projects, issues, and comments.
- **Contributor Management**: Add, list, and remove contributors to projects.
- **Issue Tracking**: Categorize, assign, and track issues by priority and status.
- **Commenting System**: Manage issue-specific comments.
- **Green Code Principles**: Optimized and efficient API.

## Tech Stack
- **Backend**: Django Rest Framework (DRF)
- **Database**: PostgreSQL (or other compatible relational databases)
- **Authentication**: JWT (using `djangorestframework-simplejwt`)
- **Documentation**: Swagger (using `drf-yasg`)

## Installation

### Prerequisites
- Python 3.10+
- pipenv
- 
### Steps
1. Clone the repository:
    ```bash
    git clone https://github.com/SallyPJ/ocp10.git
    cd softdesk
    ```
2. Set up the virtual environment and install dependencies using pipenv:
    ```bash
    pipenv install --dev
    ```
3. Activate the virtual environment:
    ```bash
    pipenv shell
    ```
4. create migrations :
    ```env
    python manage.py make migrations
    ```
5. Apply migrations:
    ```bash
    python manage.py migrate
    ```
6. Run the development server:
    ```bash
    python manage.py runserver
    ```

## Endpoints

### Documentation

http://localhost:8000/swagger/

### Authentication
- `POST /api/token/`: Obtain JWT tokens.
- `POST /api/token/refresh/`: Refresh JWT tokens.

### Users
- `GET /users/`: List all users (Admin only).
- `POST /users/`: Create a new user (accessible to everyone).
- `GET /users/{id}/`: Retrieve a specific user's details (Admin or the user themselves).
- `PATCH /users/{id}/`: Update a user's details (Admin or the user themselves).
- `DELETE /users/{id}/`: Delete a user (Admin or the user themselves).
### Projects
- `GET /api/projects/`: List all projects accessible to the user.
- `POST /api/projects/`: Create a new project.
- `GET /api/projects/{id}/`: Retrieve project details.
- `PUT /api/projects/{id}/`: Update a project.
- `PATCH /api/projects/{id}/`: Partially update a project.
- `DELETE /api/projects/{id}/`: Delete a project.

### Issues
- `GET /api/projects/{project_pk}/issues/`: List all issues in a project.
- `POST /api/projects/{project_pk}/issues/`: Create a new issue.
- `GET /api/projects/{project_pk}/issues/{id}/`: Retrieve issue details.
- `PUT /api/projects/{project_pk}/issues/{id}/`: Update an issue.
- `PATCH /api/projects/{project_pk}/issues/{id}/`: Partially update an issue.
- `DELETE /api/projects/{project_pk}/issues/{id}/`: Delete an issue.

### Comments
- `GET /api/projects/{project_pk}/issues/{issue_pk}/comments/`: List all comments on an issue.
- `POST /api/projects/{project_pk}/issues/{issue_pk}/comments/`: Create a new comment.
- `GET /api/projects/{project_pk}/issues/{issue_pk}/comments/{id}/`: Retrieve comment details.
- `PUT /api/projects/{project_pk}/issues/{issue_pk}/comments/{id}/`: Update a comment.
- `PATCH /api/projects/{project_pk}/issues/{issue_pk}/comments/{id}/`: Partially update a comment.
- `DELETE /api/projects/{project_pk}/issues/{issue_pk}/comments/{id}/`: Delete a comment.

### Contributors
- `GET /api/projects/{project_pk}/contributors/`: List all contributors to a project.
- `POST /api/projects/{project_pk}/contributors/`: Add a contributor to a project.
- `DELETE /api/projects/{project_pk}/contributors/{id}/`: Remove a contributor from a project.

## Permissions

### User Roles
1. **Admin**: Full access to all resources.
2. **Project Manager**: Can manage projects and contributors.
3. **Contributor**: Can create, update, and delete issues and comments in their projects.

### Permissions Matrix
| Action                 | Admin       | Project Manager | Contributor |
|------------------------|-------------|-----------------|-------------|
| Create Project         | ✅          | ✅              | ❌          |
| Update Project         | ✅          | ✅              | ❌          |
| Delete Project         | ✅          | ✅              | ❌          |
| Create Issue           | ✅          | ✅              | ✅          |
| Update Issue           | ✅          | ❌              | ✅ (Author) |
| Delete Issue           | ✅          | ❌              | ✅ (Author) |
| Add Contributor        | ✅          | ✅              | ❌          |



## License
This project is licensed under the MIT License.

