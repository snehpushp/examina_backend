# Examina Backend - System Manual

## Overview

Examina Backend is a comprehensive examination management system built with FastAPI, designed to handle large-scale competitive examinations. The system provides APIs for managing exams, papers, questions, and Computer-Based Testing (CBT) environments.

## System Architecture

### Technology Stack
- **Backend Framework**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Async Operations**: asyncpg, asyncio
- **Validation**: Pydantic
- **Authentication**: JWT (extensible)
- **Documentation**: Auto-generated OpenAPI/Swagger
- **Containerization**: Docker

### Architecture Patterns
- **Layered Architecture**: Clear separation between API, Service, and Data layers
- **Dependency Injection**: FastAPI's dependency system for service management
- **Repository Pattern**: Data access abstraction through SQLAlchemy models
- **Service Layer**: Business logic encapsulation
- **Schema Validation**: Pydantic models for request/response validation

## System Components

### 1. API Layer (`app/api/`)
- **Purpose**: Handle HTTP requests and responses
- **Components**:
  - `v1/endpoints/`: REST API endpoints
  - `v1/routers.py`: Route configuration and custom route handlers
  - `v1/dependencies.py`: Dependency injection setup

### 2. Core Layer (`app/core/`)
- **Purpose**: Business logic and data management
- **Components**:
  - `models/`: SQLAlchemy database models
  - `services/`: Business logic services
  - `schemas/`: Internal Pydantic schemas
  - `db/`: Database configuration and connection management

### 3. Configuration (`app/config.py`, `app/core/config.py`)
- **Purpose**: Application and database configuration
- **Features**:
  - Environment-based settings
  - Database connection parameters
  - Application metadata

## Data Model

### Hierarchical Structure
```
Exams (Root Level)
├── Papers (Specific instances)
│   ├── Templates (Exam patterns)
│   ├── Sections (Subject divisions)
│   │   └── Sub-sections (Topic divisions)
│   │       └── Questions
│   │           ├── Options (MCQ/MSQ)
│   │           └── Range Answers (NAT)
└── Languages (Multi-language support)
```

### Key Entities

#### 1. Exams
- **Purpose**: Root level exam categories (JEE, NEET, UPSC)
- **Features**: Soft delete, active/inactive status
- **Relationships**: One-to-many with Papers

#### 2. Papers
- **Purpose**: Specific exam instances (JEE 2023 Set A)
- **Features**: Status management (Draft, Published, Archived)
- **Relationships**: Belongs to Exam, has Templates, Sections

#### 3. Questions
- **Purpose**: Individual test questions
- **Types**: MCQ, MSQ, NAT (Numerical Answer Type)
- **Features**: Difficulty scoring, subject tagging, multi-language support

#### 4. Templates
- **Purpose**: Exam pattern configuration
- **Features**: JSON-based settings, instructions, time limits

## API Endpoints

### Exam Management
```http
GET    /api/v1/exams/                    # List all exams
POST   /api/v1/exams/                    # Create exams (bulk)
GET    /api/v1/exams/{id}/papers         # Get papers for exam
PATCH  /api/v1/exams/{id}/active         # Update exam status
DELETE /api/v1/exams/{id}                # Delete exam
```

### Paper Management
```http
GET    /api/v1/paper/{id}                # Get paper for CBT
GET    /api/v1/paper/{id}/solution       # Get paper solutions
POST   /api/v1/exams/{id}/paper          # Create new paper
PATCH  /api/v1/paper/{id}/status         # Update paper status
PATCH  /api/v1/paper/{id}                # Update paper details
DELETE /api/v1/paper/{id}                # Delete paper
```

### Question Management
```http
POST   /api/v1/questions/create          # Create single question
POST   /api/v1/questions/bulk_create     # Create multiple questions
```

### Section Management
```http
PATCH  /api/v1/sections/{id}             # Update section
PATCH  /api/v1/sub_sections/{id}         # Update sub-section
PATCH  /api/v1/sub_sections/{id}/{q_id}  # Update question in sub-section
```

## Configuration Management

### Environment Variables

#### Application Settings
```env
PROJECT_NAME=Examina Backend
PROJECT_DEBUG=False
PROJECT_API_VERSION=1.0.0
PROJECT_HOST=0.0.0.0
PROJECT_PORT=8001
AUDIT_LOG_LOCATION=/var/log/examina/
```

#### Database Settings
```env
POSTGRES_USER=examina_user
POSTGRES_PASSWORD=secure_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=examina_db
POSTGRES_DATABASE_SCHEMA=public
```

## Deployment Guide

### Development Environment
1. **Setup virtual environment**
   ```bash
   poetry install
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

3. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

4. **Start development server**
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

### Production Deployment

#### Docker Deployment
```bash
# Build image
docker build -t examina-backend .

# Run container
docker run -d \
  --name examina-backend \
  -p 8001:8001 \
  -e POSTGRES_HOST=your-db-host \
  -e POSTGRES_USER=your-db-user \
  -e POSTGRES_PASSWORD=your-db-password \
  examina-backend
```

#### Direct Deployment
```bash
# Install dependencies
poetry install --no-dev

# Run with production server
poetry run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Security Considerations

### Data Protection
- **SQL Injection**: Protected by SQLAlchemy ORM
- **Input Validation**: Pydantic schema validation
- **CORS**: Configurable cross-origin policies
- **Environment Variables**: Sensitive data isolation

### Authentication (Extensible)
- **JWT Tokens**: Ready for implementation
- **Role-Based Access**: Database schema supports user roles
- **API Key Authentication**: Configurable for service-to-service communication

## Performance Optimization

### Database
- **Connection Pooling**: SQLAlchemy connection pooling
- **Async Operations**: Full async/await implementation
- **Indexes**: Optimized database indexes for queries
- **Soft Deletes**: Data preservation without hard deletes

### API
- **Pagination**: Built-in pagination support
- **Response Compression**: Configurable compression
- **Caching**: Redis-ready architecture (extensible)

## Monitoring and Logging

### Logging
- **Structured Logging**: JSON-formatted logs
- **Log Levels**: Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- **Audit Trail**: User action logging capability

### Health Checks
- **Database Health**: Connection status monitoring
- **API Health**: Endpoint availability checks
- **System Metrics**: Performance monitoring (extensible)

## Testing Strategy

### Test Types
- **Unit Tests**: Service layer testing
- **Integration Tests**: API endpoint testing
- **Database Tests**: Model and query testing

### Test Configuration
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/test_exams.py
```

## Troubleshooting

### Common Issues

#### Database Connection
```python
# Check database connection
from app.core.db import get_db_session
async with get_db_session() as session:
    result = await session.execute("SELECT 1")
    print(result.scalar())
```

#### Migration Issues
```bash
# Reset migrations
alembic downgrade base
alembic upgrade head
```

#### Performance Issues
- Monitor database query performance
- Check connection pool settings
- Review async/await usage
- Analyze API response times

## Maintenance

### Regular Tasks
- **Database Backup**: Regular PostgreSQL backups
- **Log Rotation**: Automated log file management
- **Dependency Updates**: Regular security updates
- **Performance Monitoring**: Regular performance reviews

### Data Management
- **Soft Delete Cleanup**: Periodic cleanup of soft-deleted records
- **Archive Management**: Moving old papers to archive status
- **Question Bank Maintenance**: Regular question review and updates
