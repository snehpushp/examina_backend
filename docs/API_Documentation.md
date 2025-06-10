# Examina Backend - API Documentation

## Overview

The Examina Backend API provides comprehensive endpoints for managing online examinations, including exam creation, paper management, question handling, and Computer-Based Testing (CBT) functionality. The API is built with FastAPI and follows RESTful principles.

## Base Information

- **Base URL**: `http://localhost:8001/v1` (Development)
- **Content-Type**: `application/json`
- **API Version**: v1
- **Documentation**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

## Authentication

Currently, the API is open for development purposes. Future versions will include:
- JWT Token Authentication
- API Key Authentication
- Role-based Access Control

## Response Format

All responses follow FastAPI's standard format. The API uses Pydantic models for request/response validation.

## HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Request successful, no content returned
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## Exam Management Endpoints

### 1. Get All Exams

**Endpoint**: `GET /v1/exams/`

**Description**: Retrieve all available exams in the system.

**Query Parameters**:
- `include_inactive` (boolean, optional): Include inactive exams (default: false)

**Example Request**:
```bash
curl -X GET "http://localhost:8001/v1/exams/?include_inactive=false"
```

**Response Model**: `List[ExamsResponseSchema]`

**Example Response**:
```json
[
    {
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "name": "JEE Main",
        "is_active": true
    },
    {
        "uuid": "550e8400-e29b-41d4-a716-446655440001",
        "name": "NEET",
        "is_active": true
    }
]
```

### 2. Create Exams (Bulk)

**Endpoint**: `POST /v1/exams/`

**Description**: Create multiple exams in a single request.

**Request Model**: `List[ExamsCreateDatabaseSchema]`

**Request Body**:
```json
[
    {
        "name": "JEE Advanced",
        "description": "Joint Entrance Examination Advanced for IIT admissions",
        "is_active": true
    },
    {
        "name": "GATE",
        "description": "Graduate Aptitude Test in Engineering",
        "is_active": false
    }
]
```

**Example Request**:
```bash
curl -X POST "http://localhost:8001/v1/exams/" \
  -H "Content-Type: application/json" \
  -d '[{"name": "UPSC", "description": "Union Public Service Commission", "is_active": true}]'
```

**Response**: Returns the created exam instances

### 3. Get Papers by Exam ID

**Endpoint**: `GET /v1/exams/{exam_id}/papers`

**Description**: Retrieve all papers for a specific exam.

**Path Parameters**:
- `exam_id` (UUID): Exam identifier

**Query Parameters**:
- `paper_status` (PapersStatusEnum, required): Filter by status (DRAFT, PUBLISHED, ARCHIVED)

**Response Model**: `List[PapersResponseSchema]`

**Example Request**:
```bash
curl -X GET "http://localhost:8001/v1/exams/550e8400-e29b-41d4-a716-446655440000/papers?paper_status=PUBLISHED"
```

**Example Response**:
```json
[
    {
        "uuid": "550e8400-e29b-41d4-a716-446655440002",
        "name": "JEE Main 2024 Session 1"
    },
    {
        "uuid": "550e8400-e29b-41d4-a716-446655440003",
        "name": "JEE Main 2024 Session 2"
    }
]
```

### 4. Create Paper for Exam

**Endpoint**: `POST /v1/exams/{exam_id}/paper`

**Description**: Create a new paper for an exam with complete structure.

**Path Parameters**:
- `exam_id` (UUID): Exam identifier

**Request Model**: `CBTRequestSchema`

**Request Body**:
```json
{
    "name": "JEE Main 2024 Session 1",
    "instructions": "Read all instructions carefully before starting the exam.",
    "year": 2024,
    "paper_set": "A",
    "language": "ENGLISH",
    "settings": {
        "total_time": 180,
        "is_calculator_allowed": false,
        "calculator_type": "NORMAL"
    },
    "sections": [
        {
            "name": "Physics",
            "section_time": 60,
            "sub_sections": [
                {
                    "name": "Mechanics",
                    "questions": [
                        {
                            "question": "A ball is thrown vertically upward...",
                            "explanation": "Using kinematic equation...",
                            "question_type": "MCQ",
                            "subject": "Physics",
                            "content_type": "NORMAL",
                            "language": "ENGLISH",
                            "difficulty": 500,
                            "positive_marks": 4.0,
                            "negative_marks": 1.0,
                            "options": [
                                {"option": "10 m", "is_correct_option": false},
                                {"option": "20 m", "is_correct_option": true}
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
```

**Response**: Returns the created paper instance

### 5. Update Exam Status

**Endpoint**: `PATCH /v1/exams/{exam_id}/active`

**Description**: Update the active status of an exam.

**Path Parameters**:
- `exam_id` (UUID): Exam identifier

**Query Parameters**:
- `is_active` (boolean, required): New active status

**Example Request**:
```bash
curl -X PATCH "http://localhost:8001/v1/exams/550e8400-e29b-41d4-a716-446655440000/active?is_active=false"
```

**Response**: Returns the updated exam instance

### 6. Delete Exam

**Endpoint**: `DELETE /v1/exams/{exam_id}`

**Description**: Soft delete an exam (marks as deleted but preserves data).

**Path Parameters**:
- `exam_id` (UUID): Exam identifier

**Example Request**:
```bash
curl -X DELETE "http://localhost:8001/v1/exams/550e8400-e29b-41d4-a716-446655440000"
```

**Response**: HTTP 204 No Content

---

## Paper Management Endpoints

### 1. Get Paper for CBT

**Endpoint**: `GET /v1/paper/{paper_id}`

**Description**: Retrieve complete paper structure for Computer-Based Testing environment.

**Path Parameters**:
- `paper_id` (UUID): Paper identifier

**Response Model**: `CBTResponseSchema`

**Example Request**:
```bash
curl -X GET "http://localhost:8001/v1/paper/550e8400-e29b-41d4-a716-446655440004"
```

**Example Response**:
```json
{
    "uuid": "550e8400-e29b-41d4-a716-446655440004",
    "name": "JEE Main 2024 Session 1",
    "instructions": "Read all instructions carefully...",
    "year": 2024,
    "paper_set": "A",
    "language": "ENGLISH",
    "settings": {
        "total_time": 180,
        "is_calculator_allowed": false,
        "calculator_type": "NORMAL"
    },
    "sections": [
        {
            "uuid": "550e8400-e29b-41d4-a716-446655440005",
            "name": "Physics",
            "section_time": 60,
            "sub_sections": [
                {
                    "uuid": "550e8400-e29b-41d4-a716-446655440006",
                    "name": "Mechanics",
                    "questions": [
                        {
                            "uuid": "550e8400-e29b-41d4-a716-446655440007",
                            "question": "A ball is thrown vertically upward...",
                            "question_type": "MCQ",
                            "content_type": "NORMAL",
                            "passage": null,
                            "positive_marks": 4.0,
                            "negative_marks": 1.0,
                            "options": [
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-446655440008",
                                    "option": "10 m"
                                },
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-446655440009",
                                    "option": "20 m"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
```

### 2. Get Paper Solutions

**Endpoint**: `GET /v1/paper/{paper_id}/solution`

**Description**: Retrieve answer key and solutions for a paper.

**Path Parameters**:
- `paper_id` (UUID): Paper identifier

**Example Request**:
```bash
curl -X GET "http://localhost:8001/v1/paper/550e8400-e29b-41d4-a716-446655440004/solution"
```

### 3. Update Paper Status

**Endpoint**: `PATCH /v1/paper/{paper_id}/status`

**Description**: Update the status of a paper (DRAFT, PUBLISHED, ARCHIVED).

**Path Parameters**:
- `paper_id` (UUID): Paper identifier

**Query Parameters**:
- `status` (PapersStatusEnum, required): New status value

**Example Request**:
```bash
curl -X PATCH "http://localhost:8001/v1/paper/550e8400-e29b-41d4-a716-446655440004/status?status=PUBLISHED"
```

### 4. Update Paper Details

**Endpoint**: `PATCH /v1/paper/{paper_id}`

**Description**: Update paper metadata and settings.

**Path Parameters**:
- `paper_id` (UUID): Paper identifier

**Request Model**: `CBTPaperBaseSchema`

**Request Body**:
```json
{
    "name": "JEE Main 2024 Session 1 - Updated",
    "instructions": "Updated instructions for the exam.",
    "year": 2024,
    "paper_set": "A",
    "language": "ENGLISH",
    "settings": {
        "total_time": 200,
        "is_calculator_allowed": true,
        "calculator_type": "SCIENTIFIC"
    }
}
```

### 5. Delete Paper

**Endpoint**: `DELETE /v1/paper/{paper_id}`

**Description**: Soft delete a paper.

**Path Parameters**:
- `paper_id` (UUID): Paper identifier

**Response**: HTTP 204 No Content

---

## Question Management Endpoints

### 1. Create Single Question

**Endpoint**: `POST /v1/questions/create`

**Description**: Create a single question with options or range answers.

**Request Model**: `QuestionsUploadSchema`

**Request Body Examples**:

**MCQ Question**:
```json
{
    "question": "What is the capital of France?",
    "explanation": "Paris is the capital and largest city of France.",
    "question_type": "MCQ",
    "content_type": "NORMAL",
    "subject": "Geography",
    "language": "ENGLISH",
    "knowledge_level": 5,
    "difficulty": 300,
    "source": "Geography Textbook",
    "tags": ["capitals", "Europe", "France"],
    "options": [
        {"option": "London", "is_correct_option": false},
        {"option": "Berlin", "is_correct_option": false},
        {"option": "Paris", "is_correct_option": true},
        {"option": "Madrid", "is_correct_option": false}
    ]
}
```

**NAT Question**:
```json
{
    "question": "Find the value of x in the equation 2x + 5 = 15",
    "explanation": "2x = 15 - 5 = 10, therefore x = 5",
    "question_type": "NAT",
    "content_type": "NORMAL",
    "subject": "Mathematics",
    "language": "ENGLISH",
    "start": 5,
    "end": 5
}
```

**Response**: Returns the created question instance

### 2. Create Multiple Questions (Bulk)

**Endpoint**: `POST /v1/questions/bulk_create`

**Description**: Create multiple questions in a single request.

**Request Model**: `List[QuestionsUploadSchema]`

**Request Body**:
```json
[
    {
        "question": "What is 2 + 2?",
        "question_type": "MCQ",
        "subject": "Mathematics",
        "content_type": "NORMAL",
        "language": "ENGLISH",
        "options": [
            {"option": "3", "is_correct_option": false},
            {"option": "4", "is_correct_option": true},
            {"option": "5", "is_correct_option": false}
        ]
    },
    {
        "question": "Find the value of x if 2x + 5 = 15",
        "question_type": "NAT",
        "subject": "Mathematics",
        "content_type": "NORMAL",
        "language": "ENGLISH",
        "start": 5,
        "end": 5
    }
]
```

**Response**: Returns the created question instances

---

## Section Management Endpoints

### 1. Update Section

**Endpoint**: `PATCH /v1/sections/{section_id}`

**Description**: Update section details like name and time allocation.

**Path Parameters**:
- `section_id` (UUID): Section identifier

**Request Model**: `SectionsUpdateDatabaseSchema`

### 2. Update Sub-Section

**Endpoint**: `PATCH /v1/sub_sections/{sub_section_id}`

**Description**: Update sub-section details.

**Path Parameters**:
- `sub_section_id` (UUID): Sub-section identifier

**Request Model**: `SubSectionsUpdateDatabaseSchema`

### 3. Update Question in Sub-Section

**Endpoint**: `PATCH /v1/sub_sections/{sub_section_id}/{question_id}`

**Description**: Update question details within a specific sub-section.

**Path Parameters**:
- `sub_section_id` (UUID): Sub-section identifier
- `question_id` (UUID): Question identifier

**Request Model**: `CBTQuestionUpdateSchema`

**Request Body**:
```json
{
    "positive_marks": 5.0,
    "negative_marks": 1.25,
    "question": "Updated question text",
    "difficulty": 600,
    "content_type": "NORMAL",
    "subject": "Physics",
    "language": "ENGLISH",
    "knowledge_level": 12,
    "source": "Updated source",
    "passage": null,
    "tags": ["updated", "physics"]
}
```

---

## Data Models

### Question Types (QuestionTypeEnum)

1. **MCQ**: Multiple Choice Question (single correct answer)
2. **MSQ**: Multiple Select Question (multiple correct answers)
3. **NAT**: Numerical Answer Type (range-based numerical answers)

### Content Types (ContentTypeEnum)

1. **NORMAL**: Standalone questions
2. **PASSAGE**: Reading comprehension based questions

### Paper Status (PapersStatusEnum)

1. **DRAFT**: Paper is being created/edited
2. **PUBLISHED**: Paper is available for testing
3. **ARCHIVED**: Paper is no longer active

### Languages (LanguageEnum)

1. **ENGLISH**: English language
2. **HINDI**: Hindi language

### Calculator Types (CalculatorTypeEnum)

1. **NORMAL**: Basic calculator
2. **SCIENTIFIC**: Scientific calculator

---

## Response Schemas

### ExamsResponseSchema
```json
{
    "uuid": "UUID",
    "name": "string",
    "is_active": "boolean"
}
```

### PapersResponseSchema
```json
{
    "uuid": "UUID",
    "name": "string"
}
```

### CBTResponseSchema
```json
{
    "uuid": "UUID",
    "name": "string",
    "instructions": "string",
    "year": "integer",
    "paper_set": "string",
    "language": "LanguageEnum",
    "settings": "CBTSettingsSchema",
    "sections": "List[CBTSectionsResponseSchema]"
}
```

### CBTQuestionsResponseSchema
```json
{
    "uuid": "UUID",
    "question": "string",
    "question_type": "QuestionTypeEnum",
    "content_type": "ContentTypeEnum",
    "passage": "string | null",
    "positive_marks": "float",
    "negative_marks": "float",
    "options": "List[CBTOptionsResponseSchema]"
}
```

---

## Validation Rules

### Question Validation
- MCQ questions must have exactly one correct option
- MSQ questions must have at least one correct option
- NAT questions must have valid numeric range (start ≤ end)
- Minimum 2 options required for MCQ/MSQ questions
- Difficulty must be between reasonable bounds
- Knowledge level represents class/grade level

### Paper Validation
- Paper names with unique constraints per exam/language/year/set
- Section time and paper time validation
- Each sub-section must have at least one question
- Positive marks must be greater than 0

---

## Error Handling

The API uses FastAPI's built-in validation and error handling. Common error responses include:

- **422 Unprocessable Entity**: Pydantic validation errors
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side errors

---

## Testing the API

### Using cURL

```bash
# Get all exams
curl -X GET "http://localhost:8001/v1/exams/"

# Create a question
curl -X POST "http://localhost:8001/v1/questions/create" \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question", "question_type": "MCQ", "subject": "Test", "content_type": "NORMAL", "language": "ENGLISH", "options": [{"option": "A", "is_correct_option": true}]}'
```

### Using Python requests

```python
import requests

# Get all exams
response = requests.get("http://localhost:8001/v1/exams/")
print(response.json())

# Create a question
question_data = {
    "question": "What is 2+2?",
    "question_type": "MCQ",
    "subject": "Mathematics",
    "content_type": "NORMAL",
    "language": "ENGLISH",
    "options": [
        {"option": "3", "is_correct_option": False},
        {"option": "4", "is_correct_option": True}
    ]
}
response = requests.post("http://localhost:8001/v1/questions/create", json=question_data)
print(response.json())
```

---

## Notes

1. **Base URL**: The actual base URL is `/v1` (not `/api/v1` as the router is included directly)
2. **Router Structure**: The API uses nested routers with proper prefixes
3. **Response Models**: All endpoints use Pydantic models for response validation
4. **Required Parameters**: Some query parameters like `paper_status` are required, not optional
5. **Configuration**: The app uses a `Configuration` class that combines all settings

---

For more detailed information and interactive testing, visit the Swagger UI documentation at `http://localhost:8001/docs` when the server is running.
