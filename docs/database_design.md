# Database Design - Examina Backend

## Overview

The Examina Backend uses PostgreSQL as the primary database with SQLAlchemy ORM for data modeling. The database is designed to support hierarchical exam structures with flexible question types and comprehensive metadata.

## Design Principles

- **Hierarchical Structure**: Exams → Papers → Sections → Sub-sections → Questions
- **Soft Deletes**: Data preservation with `is_deleted` flags
- **UUID Primary Keys**: Scalable and distributed system friendly
- **Normalized Design**: Minimized data redundancy
- **Flexible Schema**: JSON fields for complex configurations
- **Multi-language Support**: Language-aware content storage

## Entity Relationship Diagram

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Exams    │    │  Templates  │    │  Languages  │
│─────────────│    │─────────────│    │─────────────│
│ uuid (PK)   │    │ uuid (PK)   │    │ uuid (PK)   │
│ name        │    │ name        │    │ name        │
│ description │    │ settings    │    └─────────────┘
│ is_active   │    │ instructions│           │
│ is_deleted  │    └─────────────┘           │
└─────────────┘           │                  │
       │                  │                  │
       │ 1:N              │                  │
       ▼                  │                  │
┌─────────────┐           │                  │
│   Papers    │           │                  │
│─────────────│           │                  │
│ uuid (PK)   │───────────┘                  │
│ exam_id(FK) │                              │
│ name        │──────────────────────────────┘
│ year        │ language_id (FK)
│ paper_set   │
│ status      │
│ template_id │
│ is_deleted  │
└─────────────┘
       │ 1:N
       ▼
┌─────────────┐
│  Sections   │
│─────────────│
│ uuid (PK)   │
│ paper_id(FK)│
│ name        │
│ section_time│
│ order       │
└─────────────┘
       │ 1:N
       ▼
┌─────────────┐    ┌─────────────┐
│SubSections  │    │  Subjects   │
│─────────────│    │─────────────│
│ uuid (PK)   │    │ uuid (PK)   │
│ section_id  │    │ name        │
│ name        │    │ is_deleted  │
│ order       │    └─────────────┘
└─────────────┘           │
       │ M:N              │
       ▼                  │
┌─────────────┐           │
│SubSection   │           │
│Questions    │           │
│─────────────│           │
│sub_section  │           │
│question_id  │           │
│positive_mark│           │
│negative_mark│           │
│ order       │           │
└─────────────┘           │
       │                  │
       ▼                  │
┌─────────────┐           │
│ Questions   │───────────┘
│─────────────│ subject_id (FK)
│ uuid (PK)   │
│ question    │
│ explanation │
│question_type│
│ content_type│
│ passage_id  │
│ difficulty  │
│ source      │
│ language_id │
│ is_deleted  │
└─────────────┘
       │ 1:N
       ▼
┌─────────────┐
│  Options    │
│─────────────│
│ uuid (PK)   │
│ question_id │
│ option      │
│ option_order│
│ is_correct  │
│ is_deleted  │
└─────────────┘
```

## Core Tables

### 1. Exams Table
**Purpose**: Root level exam categories (JEE, NEET, UPSC, CAT, etc.)

```sql
CREATE TABLE exams (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(128) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features**:
- Soft delete support
- Active/inactive status management
- Timestamps for audit trail

### 2. Papers Table
**Purpose**: Specific exam instances with year and set information

```sql
CREATE TABLE papers (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID NOT NULL REFERENCES exams(uuid),
    name VARCHAR(128) NOT NULL,
    year INTEGER NOT NULL,
    paper_set VARCHAR(128),
    status exam_status_enum DEFAULT 'DRAFT',
    template_id UUID NOT NULL REFERENCES templates(uuid),
    language_id UUID NOT NULL REFERENCES language(uuid),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_exam_paper_set UNIQUE (exam_id, language_id, year, name, paper_set, is_deleted)
);
```

**Key Features**:
- Unique constraint preventing duplicate papers
- Status management (Draft, Published, Archived)
- Language support
- Template-based configuration

### 3. Templates Table
**Purpose**: Exam pattern and configuration storage

```sql
CREATE TABLE templates (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(128) NOT NULL,
    settings JSON NOT NULL,
    instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Settings JSON Structure**:
```json
{
    "total_time": 180,
    "is_calculator_allowed": true,
    "calculator_type": "scientific",
    "section_switching_allowed": false,
    "review_allowed": true,
    "partial_marking": false
}
```

### 4. Sections Table
**Purpose**: Major subject divisions within papers

```sql
CREATE TABLE sections (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id UUID NOT NULL REFERENCES papers(uuid),
    name VARCHAR(128) NOT NULL,
    section_time INTEGER NOT NULL,
    order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. Sub-Sections Table
**Purpose**: Topic-wise subdivisions within sections

```sql
CREATE TABLE sub_sections (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    section_id UUID NOT NULL REFERENCES sections(uuid),
    name VARCHAR(128) NOT NULL,
    order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6. Questions Table
**Purpose**: Individual test questions with metadata

```sql
CREATE TABLE questions (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    explanation TEXT,
    question_type question_type_enum NOT NULL,
    content_type content_type_enum NOT NULL,
    passage_id UUID REFERENCES passages(uuid),
    subject_id UUID NOT NULL REFERENCES subjects(uuid),
    knowledge_level INTEGER,
    difficulty INTEGER DEFAULT 500,
    source VARCHAR(128),
    language_id UUID NOT NULL REFERENCES language(uuid),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Question Types**:
- `MCQ`: Multiple Choice Question (single correct)
- `MSQ`: Multiple Select Question (multiple correct)
- `NAT`: Numerical Answer Type (range-based)

**Content Types**:
- `NORMAL`: Standalone questions
- `PASSAGE`: Reading comprehension based

### 7. Options Table
**Purpose**: Multiple choice options for MCQ/MSQ questions

```sql
CREATE TABLE options (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(uuid),
    option TEXT NOT NULL,
    option_order INTEGER NOT NULL,
    is_correct_option BOOLEAN NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_option_order UNIQUE (question_id, option_order)
);
```

### 8. Range Answers Table
**Purpose**: Numerical range answers for NAT questions

```sql
CREATE TABLE range_answers (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(uuid),
    start FLOAT NOT NULL,
    end FLOAT NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Supporting Tables

### 9. Subjects Table
```sql
CREATE TABLE subjects (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(128) NOT NULL UNIQUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 10. Passages Table
```sql
CREATE TABLE passages (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passage_text TEXT NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 11. Tags System
```sql
CREATE TABLE tags (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tag_name VARCHAR(128) NOT NULL,
    subject_id UUID NOT NULL REFERENCES subjects(uuid),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE question_tags (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(uuid),
    tag_id UUID NOT NULL REFERENCES tags(uuid),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 12. Language Support
```sql
CREATE TABLE language (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name language_enum NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Junction Tables

### 13. Sub-Section Questions (Many-to-Many)
```sql
CREATE TABLE sub_section_questions (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sub_section_id UUID NOT NULL REFERENCES sub_sections(uuid),
    question_id UUID NOT NULL REFERENCES questions(uuid),
    positive_marks FLOAT NOT NULL,
    negative_marks FLOAT DEFAULT 0.0,
    order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_sub_section_question UNIQUE (sub_section_id, question_id),
    CONSTRAINT unique_sub_section_order UNIQUE (sub_section_id, order)
);
```

## Enumerations

### Status Enums
```sql
CREATE TYPE exam_status_enum AS ENUM ('DRAFT', 'PUBLISHED', 'ARCHIVED');
CREATE TYPE question_type_enum AS ENUM ('MCQ', 'MSQ', 'NAT');
CREATE TYPE content_type_enum AS ENUM ('NORMAL', 'PASSAGE');
CREATE TYPE calculator_type_enum AS ENUM ('NORMAL', 'SCIENTIFIC');
CREATE TYPE language_enum AS ENUM ('ENGLISH', 'HINDI');
```

## Indexes and Performance

### Primary Indexes
```sql
-- Frequently queried foreign keys
CREATE INDEX idx_papers_exam_id ON papers(exam_id);
CREATE INDEX idx_sections_paper_id ON sections(paper_id);
CREATE INDEX idx_sub_sections_section_id ON sub_sections(section_id);
CREATE INDEX idx_questions_subject_id ON questions(subject_id);

-- Soft delete queries
CREATE INDEX idx_exams_active ON exams(is_active) WHERE is_deleted = FALSE;
CREATE INDEX idx_papers_status ON papers(status) WHERE is_deleted = FALSE;

-- Search optimization
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_questions_type ON questions(question_type);
```

### Composite Indexes
```sql
-- Paper filtering
CREATE INDEX idx_papers_exam_status ON papers(exam_id, status) WHERE is_deleted = FALSE;

-- Question filtering
CREATE INDEX idx_questions_subject_type ON questions(subject_id, question_type) WHERE is_deleted = FALSE;
```

## Data Constraints

### Business Rules
1. **Unique Papers**: No duplicate papers for same exam, language, year, and set
2. **Question Ordering**: Questions within sub-sections must have unique order
3. **Option Ordering**: Options within questions must have unique order
4. **Positive Marking**: All questions must have non-negative positive marks
5. **Correct Options**: MCQ questions must have exactly one correct option

### Referential Integrity
- All foreign key relationships maintain referential integrity
- Cascade deletes are implemented through soft delete patterns
- Orphaned records are prevented through constraints

## Scalability Considerations

### Partitioning Strategy
```sql
-- Partition papers by year for better performance
CREATE TABLE papers_2023 PARTITION OF papers
FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE papers_2024 PARTITION OF papers
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### Archival Strategy
- Move old papers to archived status
- Implement data retention policies
- Periodic cleanup of soft-deleted records

## Backup and Recovery

### Backup Strategy
```bash
# Full database backup
pg_dump -h localhost -U examina_user -d examina_db > backup_$(date +%Y%m%d).sql

# Table-specific backups
pg_dump -h localhost -U examina_user -d examina_db -t questions > questions_backup.sql
```

### Recovery Procedures
```sql
-- Point-in-time recovery
SELECT pg_start_backup('daily_backup');
-- Copy data files
SELECT pg_stop_backup();
```

## Security Considerations

### Row-Level Security (Future Enhancement)
```sql
-- Enable RLS for multi-tenant support
ALTER TABLE papers ENABLE ROW LEVEL SECURITY;

-- Create policies for data isolation
CREATE POLICY paper_access_policy ON papers
FOR ALL TO application_role
USING (organization_id = current_setting('app.current_organization_id')::uuid);
```

### Audit Trail
- All tables include `created_at` and `updated_at` timestamps
- Soft delete functionality preserves data history
- Future enhancement: detailed audit log table

This database design provides a robust foundation for the Examina Backend system, supporting complex exam structures while maintaining performance and data integrity.
