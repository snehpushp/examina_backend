# Data Contract - Examina Backend API

## Overview

This document defines the data contracts for the Examina Backend API, including request/response schemas, validation rules, and API specifications. The API follows RESTful principles and uses JSON for data exchange.

## Base URL Structure

```
Production: https://api.examina.com/api/v1
Development: http://localhost:8001/api/v1
```

## Authentication

The API supports extensible authentication mechanisms:
- **API Key**: For service-to-service communication
- **JWT Tokens**: For user authentication (future implementation)
- **OAuth 2.0**: For third-party integrations (future implementation)

## Common Data Types

### UUID Format
All entity identifiers use UUID v4 format:
```json
{
    "uuid": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Timestamp Format
All timestamps follow ISO 8601 format:
```json
{
    "created_at": "2023-12-01T10:30:00Z",
    "updated_at": "2023-12-01T15:45:30Z"
}
```

### Pagination
List endpoints support pagination:
```json
{
    "items": [...],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5
}
```

## Enumerations

### Question Types
```json
{
    "MCQ": "Multiple Choice Question (single correct)",
    "MSQ": "Multiple Select Question (multiple correct)",
    "NAT": "Numerical Answer Type (range-based)"
}
```

### Content Types
```json
{
    "NORMAL": "Standalone question",
    "PASSAGE": "Reading comprehension based question"
}
```

### Paper Status
```json
{
    "DRAFT": "Paper is being created/edited",
    "PUBLISHED": "Paper is available for testing",
    "ARCHIVED": "Paper is no longer active"
}
```

### Languages
```json
{
    "ENGLISH": "English language",
    "HINDI": "Hindi language"
}
```

### Calculator Types
```json
{
    "NORMAL": "Basic calculator",
    "SCIENTIFIC": "Scientific calculator"
}
```

## API Endpoints

## 1. Exam Management

### GET /exams
**Purpose**: Retrieve all available exams

**Query Parameters**:
- `include_inactive` (boolean, optional): Include inactive exams (default: false)

**Response**:
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

### POST /exams
**Purpose**: Create multiple exams in bulk

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

**Response**: HTTP 201 Created
```json
{
    "message": "Exams created successfully",
    "count": 2
}
```

### GET /exams/{exam_id}/papers
**Purpose**: Get all papers for a specific exam

**Path Parameters**:
- `exam_id` (UUID): Exam identifier

**Query Parameters**:
- `paper_status` (enum): Filter by paper status (DRAFT, PUBLISHED, ARCHIVED)

**Response**:
```json
[
    {
        "uuid": "550e8400-e29b-41d4-a716-446655440002",
        "name": "JEE Main 2023 Session 1"
    },
    {
        "uuid": "550e8400-e29b-41d4-a716-446655440003",
        "name": "JEE Main 2023 Session 2"
    }
]
```

### PATCH /exams/{exam_id}/active
**Purpose**: Update exam active status

**Path Parameters**:
- `exam_id` (UUID): Exam identifier

**Query Parameters**:
- `is_active` (boolean): New active status

**Response**: HTTP 200 OK
```json
{
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "JEE Main",
    "is_active": false
}
```

### DELETE /exams/{exam_id}
**Purpose**: Soft delete an exam

**Path Parameters**:
- `exam_id` (UUID): Exam identifier

**Response**: HTTP 204 No Content

## 2. Paper Management

### POST /exams/{exam_id}/paper
**Purpose**: Create a new paper for an exam

**Path Parameters**:
- `exam_id` (UUID): Exam identifier

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
        "calculator_type": null,
        "section_switching_allowed": true,
        "review_allowed": true
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
                            "question": "A ball is thrown vertically upward with initial velocity 20 m/s. Find the maximum height reached.",
                            "explanation": "Using kinematic equation: v² = u² + 2as",
                            "question_type": "MCQ",
                            "subject": "Physics",
                            "content_type": "NORMAL",
                            "language": "ENGLISH",
                            "difficulty": 500,
                            "positive_marks": 4.0,
                            "negative_marks": 1.0,
                            "options": [
                                {"option": "10 m", "is_correct_option": false},
                                {"option": "20 m", "is_correct_option": true},
                                {"option": "30 m", "is_correct_option": false},
                                {"option": "40 m", "is_correct_option": false}
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
```

**Response**: HTTP 201 Created
```json
{
    "message": "Paper created successfully",
    "paper_id": "550e8400-e29b-41d4-a716-446655440004"
}
```

### GET /paper/{paper_id}
**Purpose**: Get paper content for CBT (Computer-Based Test) environment

**Path Parameters**:
- `paper_id` (UUID): Paper identifier

**Response**:
```json
{
    "uuid": "550e8400-e29b-41d4-a716-446655440004",
    "name": "JEE Main 2024 Session 1",
    "instructions": "Read all instructions carefully before starting the exam.",
    "year": 2024,
    "paper_set": "A",
    "language": "ENGLISH",
    "settings": {
        "total_time": 180,
        "is_calculator_allowed": false,
        "calculator_type": null,
        "section_switching_allowed": true,
        "review_allowed": true
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
                            "question": "A ball is thrown vertically upward with initial velocity 20 m/s. Find the maximum height reached.",
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
                                },
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-44665544000a",
                                    "option": "30 m"
                                },
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-44665544000b",
                                    "option": "40 m"
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

### GET /paper/{paper_id}/solution
**Purpose**: Get paper solutions and answer keys

**Path Parameters**:
- `paper_id` (UUID): Paper identifier

**Response**:
```json
{
    "paper_id": "550e8400-e29b-41d4-a716-446655440004",
    "solutions": [
        {
            "question_id": "550e8400-e29b-41d4-a716-446655440007",
            "question": "A ball is thrown vertically upward with initial velocity 20 m/s. Find the maximum height reached.",
            "correct_answer": {
                "type": "MCQ",
                "option_id": "550e8400-e29b-41d4-a716-446655440009",
                "option_text": "20 m"
            },
            "explanation": "Using kinematic equation: v² = u² + 2as. At maximum height, v = 0. So, 0 = 20² - 2×10×h. Therefore, h = 400/20 = 20 m.",
            "positive_marks": 4.0,
            "negative_marks": 1.0
        }
    ]
}
```

### PATCH /paper/{paper_id}/status
**Purpose**: Update paper status

**Path Parameters**:
- `paper_id` (UUID): Paper identifier

**Query Parameters**:
- `status` (enum): New status (DRAFT, PUBLISHED, ARCHIVED)

**Response**: HTTP 200 OK
```json
{
    "uuid": "550e8400-e29b-41d4-a716-446655440004",
    "status": "PUBLISHED",
    "updated_at": "2023-12-01T15:45:30Z"
}
```

### PATCH /paper/{paper_id}
**Purpose**: Update paper details

**Path Parameters**:
- `paper_id` (UUID): Paper identifier

**Request Body**:
```json
{
    "name": "JEE Main 2024 Session 1 - Updated",
    "instructions": "Updated instructions for the exam.",
    "settings": {
        "total_time": 200,
        "is_calculator_allowed": true,
        "calculator_type": "SCIENTIFIC"
    }
}
```

**Response**: HTTP 200 OK
```json
{
    "message": "Paper updated successfully",
    "updated_at": "2023-12-01T15:45:30Z"
}
```

### DELETE /paper/{paper_id}
**Purpose**: Soft delete a paper

**Path Parameters**:
- `paper_id` (UUID): Paper identifier

**Response**: HTTP 204 No Content

## 3. Question Management

### POST /questions/create
**Purpose**: Create a single question

**Request Body**:
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

**Response**: HTTP 201 Created
```json
{
    "message": "Question created successfully",
    "question_id": "550e8400-e29b-41d4-a716-44665544000c"
}
```

### POST /questions/bulk_create
**Purpose**: Create multiple questions in bulk

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

**Response**: HTTP 201 Created
```json
{
    "message": "Questions created successfully",
    "count": 2,
    "question_ids": [
        "550e8400-e29b-41d4-a716-44665544000d",
        "550e8400-e29b-41d4-a716-44665544000e"
    ]
}
```

## 4. Section Management

### PATCH /sections/{section_id}
**Purpose**: Update section details

**Path Parameters**:
- `section_id` (UUID): Section identifier

**Request Body**:
```json
{
    "name": "Advanced Physics",
    "section_time": 90
}
```

**Response**: HTTP 200 OK
```json
{
    "message": "Section updated successfully",
    "updated_at": "2023-12-01T15:45:30Z"
}
```

### PATCH /sub_sections/{sub_section_id}
**Purpose**: Update sub-section details

**Path Parameters**:
- `sub_section_id` (UUID): Sub-section identifier

**Request Body**:
```json
{
    "name": "Quantum Mechanics",
    "order": 2
}
```

**Response**: HTTP 200 OK
```json
{
    "message": "Sub-section updated successfully",
    "updated_at": "2023-12-01T15:45:30Z"
}
```

### PATCH /sub_sections/{sub_section_id}/{question_id}
**Purpose**: Update question within a sub-section

**Path Parameters**:
- `sub_section_id` (UUID): Sub-section identifier
- `question_id` (UUID): Question identifier

**Request Body**:
```json
{
    "positive_marks": 5.0,
    "negative_marks": 1.25,
    "question": "Updated question text",
    "difficulty": 600
}
```

**Response**: HTTP 200 OK
```json
{
    "message": "Question updated successfully",
    "updated_at": "2023-12-01T15:45:30Z"
}
```

## Question Data Structures

### MCQ/MSQ Questions
```json
{
    "question": "Which of the following are prime numbers?",
    "explanation": "Prime numbers are natural numbers greater than 1 that have no positive divisors other than 1 and themselves.",
    "question_type": "MSQ",
    "content_type": "NORMAL",
    "subject": "Mathematics",
    "language": "ENGLISH",
    "knowledge_level": 8,
    "difficulty": 400,
    "source": "Number Theory Textbook",
    "tags": ["prime numbers", "number theory"],
    "options": [
        {"option": "2", "is_correct_option": true},
        {"option": "3", "is_correct_option": true},
        {"option": "4", "is_correct_option": false},
        {"option": "5", "is_correct_option": true}
    ]
}
```

### NAT (Numerical Answer Type) Questions
```json
{
    "question": "Find the value of x in the equation 3x² - 12x + 9 = 0",
    "explanation": "Using quadratic formula or factoring: 3(x² - 4x + 3) = 3(x-1)(x-3) = 0",
    "question_type": "NAT",
    "content_type": "NORMAL",
    "subject": "Mathematics",
    "language": "ENGLISH",
    "knowledge_level": 10,
    "difficulty": 500,
    "source": "Algebra Textbook",
    "tags": ["quadratic equations", "algebra"],
    "start": 1,
    "end": 3
}
```

### Passage-Based Questions
```json
{
    "question": "According to the passage, what is the main cause of climate change?",
    "explanation": "The passage clearly states that greenhouse gas emissions are the primary driver.",
    "question_type": "MCQ",
    "content_type": "PASSAGE",
    "passage": "Climate change is primarily caused by increased greenhouse gas emissions from human activities. These gases trap heat in the atmosphere, leading to global warming...",
    "subject": "Environmental Science",
    "language": "ENGLISH",
    "knowledge_level": 12,
    "difficulty": 350,
    "options": [
        {"option": "Solar radiation", "is_correct_option": false},
        {"option": "Greenhouse gas emissions", "is_correct_option": true},
        {"option": "Ocean currents", "is_correct_option": false},
        {"option": "Volcanic activity", "is_correct_option": false}
    ]
}
```

## Error Responses

### Standard Error Format
```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Request validation failed",
        "details": [
            {
                "field": "question_type",
                "message": "Invalid question type. Must be one of: MCQ, MSQ, NAT"
            }
        ]
    },
    "timestamp": "2023-12-01T15:45:30Z",
    "path": "/api/v1/questions/create"
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Request data validation failed
- `NOT_FOUND`: Requested resource not found
- `DUPLICATE_ENTRY`: Attempt to create duplicate resource
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `INTERNAL_ERROR`: Server-side error

## Rate Limiting

API endpoints are rate-limited to ensure fair usage:
- **Standard endpoints**: 1000 requests per hour per API key
- **Bulk operations**: 100 requests per hour per API key
- **File uploads**: 50 requests per hour per API key

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1701436800
```

## Versioning

The API uses URL versioning:
- Current version: `v1`
- Future versions: `v2`, `v3`, etc.
- Backward compatibility maintained for at least 12 months

## Data Validation Rules

### Question Validation
1. **MCQ Questions**: Must have 2-6 options with exactly one correct option
2. **MSQ Questions**: Must have 2-6 options with at least one correct option
3. **NAT Questions**: Must have valid numeric range (start ≤ end)
4. **Difficulty**: Integer between 100-1000 (Elo rating system)
5. **Knowledge Level**: Integer between 1-15 (class/grade level)

### Paper Validation
1. **Unique Constraint**: No duplicate papers for same exam, language, year, and set
2. **Time Limits**: Section time must not exceed total paper time
3. **Question Count**: Each sub-section must have at least one question
4. **Marking Scheme**: Positive marks must be greater than 0

### Exam Validation
1. **Name Uniqueness**: Exam names must be unique within the system
2. **Status Consistency**: Only published papers can belong to active exams

This data contract ensures consistent and reliable communication between clients and the Examina Backend API.
