from enum import Enum


class IOrderEnum(Enum):
    asc: str = "asc"
    desc: str = "desc"


class HTTPMethodEnum(Enum):
    GET = "get"
    POST = "post"
    PATCH = "patch"


class QuestionTypeEnum(Enum):
    MCQ = "MCQ"
    MSQ = "MSQ"
    NAT = "NAT"


class ContentTypeEnum(Enum):
    NORMAL = "normal"
    PASSAGE = "passage"


class PapersStatusEnum(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CalculatorTypeEnum(Enum):
    NORMAL = "normal"
    SCIENTIFIC = "scientific"


class LanguageEnum(Enum):
    ENGLISH = "English"
    HINDI = "Hindi"
