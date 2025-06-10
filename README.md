# Examina Backend

A robust, scalable FastAPI-based backend system for online examination management, designed to support competitive exams like JEE, NEET, UPSC, CAT, GATE, and more.

## 🚀 Features

- **Exam Management**: Create and manage different types of competitive exams
- **Paper Organization**: Support for multiple papers per exam with different sets and years
- **Question Bank**: Comprehensive question management with support for:
  - Multiple Choice Questions (MCQ)
  - Multiple Select Questions (MSQ)
  - Numerical Answer Type (NAT)
- **Sectional Structure**: Hierarchical organization with sections and sub-sections
- **Multi-language Support**: English and Hindi language support
- **Paper Status Management**: Draft, Published, and Archived states
- **CBT Environment**: Computer-Based Test interface support
- **Solution Management**: Answer key and solution retrieval
- **Flexible Scoring**: Configurable positive and negative marking

## 🛠 Tech Stack

- **Framework**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Async Support**: Full async/await implementation with asyncpg
- **Validation**: Pydantic models for request/response validation
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Containerization**: Docker support
- **Code Quality**: Pre-commit hooks, Black formatter, isort

## 📋 Prerequisites

- Python 3.9+
- Poetry (for dependency management)
- PostgreSQL database
- Docker (optional)

## 🚀 Quick Start

### Using Poetry (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/snehpushp/examina_backend.git
   cd examina_backend
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Set up environment variables**
   Create a `.env` file with the following variables:
   ```env
   PROJECT_NAME=Examina Backend
   PROJECT_DEBUG=True
   PROJECT_API_VERSION=1.0.0
   PROJECT_HOST=0.0.0.0
   PROJECT_PORT=8001
   AUDIT_LOG_LOCATION=/var/log/examina/

   POSTGRES_USER=your_db_user
   POSTGRES_PASSWORD=your_db_password
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DATABASE=examina_db
   POSTGRES_DATABASE_SCHEMA=public
   ```

4. **Run the application**
   ```bash
   python app/main.py
   ```

### Using Docker

1. **Build and run with Docker**
   ```bash
   docker build -t examina-backend .
   docker run -p 8001:8001 examina-backend
   ```

## 📚 API Documentation

Once the server is running, access the interactive API documentation at:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

## 🏗 Project Structure

```
examina_backend/
├── app/
│   ├── api/                    # API layer
│   │   └── v1/
│   │       ├── endpoints/      # API endpoints
│   │       │   ├── exams.py   # Exam management endpoints
│   │       │   ├── papers.py  # Paper management endpoints
│   │       │   └── questions.py # Question management endpoints
│   │       ├── dependencies.py # Dependency injection
│   │       └── routers.py     # Route configuration
│   ├── core/                  # Core business logic
│   │   ├── models/           # SQLAlchemy database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic services
│   │   └── db/              # Database configuration
│   ├── utils/               # Utility functions
│   ├── config.py           # Application configuration
│   ├── enums.py            # System enumerations
│   ├── schemas.py          # API schemas
│   └── main.py             # FastAPI application entry point
├── docs/                   # Documentation
├── pyproject.toml         # Poetry configuration
├── Dockerfile            # Docker configuration
└── README.md            # This file
```

## 🗄 Database Schema

The system uses a hierarchical structure for exam organization:

```
Exams (JEE, NEET, UPSC)
└── Papers (JEE 2023 Set A, NEET 2023)
    └── Sections (Physics, Chemistry, Biology)
        └── Sub-sections (Mechanics, Thermodynamics)
            └── Questions (MCQ, MSQ, NAT)
                └── Options/Answers
```

### Key Models:
- **ExamsModel**: Root level exam types
- **PapersModel**: Specific exam instances
- **SectionsModel**: Major subject divisions
- **SubSectionsModel**: Topic-wise subdivisions
- **QuestionsModel**: Individual questions
- **OptionsModel**: Multiple choice options

## 🔌 API Endpoints

### Exams Management
- `GET /api/v1/exams/` - List all exams
- `POST /api/v1/exams/` - Create new exams
- `GET /api/v1/exams/{exam_id}/papers` - Get papers for an exam
- `PATCH /api/v1/exams/{exam_id}/active` - Update exam status
- `DELETE /api/v1/exams/{exam_id}` - Delete exam

### Papers Management
- `GET /api/v1/paper/{paper_id}` - Get paper for CBT
- `GET /api/v1/paper/{paper_id}/solution` - Get paper solutions
- `PATCH /api/v1/paper/{paper_id}/status` - Update paper status
- `PATCH /api/v1/paper/{paper_id}` - Update paper details
- `DELETE /api/v1/paper/{paper_id}` - Delete paper

### Questions Management
- `POST /api/v1/questions/create` - Create single question
- `POST /api/v1/questions/bulk_create` - Create multiple questions

## ⚙️ Configuration

The application supports environment-based configuration through Pydantic Settings:

- **App Settings**: Project name, debug mode, API version
- **Database Settings**: PostgreSQL connection parameters
- **Security Settings**: Authentication and authorization (extensible)

## 🧪 Development

### Code Quality Tools

The project includes pre-commit hooks for:
- **Black**: Code formatting (120 character line length)
- **isort**: Import sorting
- **Pre-commit**: Git hooks for code quality

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black app/
poetry run isort app/
```

## 🐳 Docker Support

The project includes multi-stage Docker builds for optimized production deployments:

```dockerfile
# Development
docker-compose up -d

# Production
docker build -t examina-backend .
docker run -p 8001:8001 examina-backend
```

## 📈 Performance Features

- **Async Database Operations**: Full async/await support with asyncpg
- **Connection Pooling**: Efficient database connection management
- **Pagination**: Built-in pagination with fastapi-pagination
- **Soft Deletes**: Data preservation with soft delete functionality
- **UUID Primary Keys**: Scalable identifier system

## 🔒 Security Features

- **CORS Configuration**: Configurable cross-origin resource sharing
- **Input Validation**: Comprehensive request validation with Pydantic
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **Environment Variable Security**: Sensitive data in environment variables

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Sneh Pushp**
- Email: pushp1999satyam@gmail.com
- GitHub: [@SnehPushp](https://github.com/SnehPushp)

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- SQLAlchemy for the powerful ORM
- Pydantic for data validation
- PostgreSQL for the robust database system
