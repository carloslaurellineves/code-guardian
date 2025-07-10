"""
Pydantic schemas for FastAPI request/response models.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum


class InputTypeEnum(str, Enum):
    """Enumeration of supported input types for API."""
    TEXT = "text"
    FILE = "file"
    GITLAB = "gitlab"


class LanguageEnum(str, Enum):
    """Enumeration of supported programming languages."""
    PYTHON = "python"
    JAVA = "java" 
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    CSHARP = "c#"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SCALA = "scala"
    UNKNOWN = "unknown"


# Request Models
class TextTestGenerationRequest(BaseModel):
    """Request model for generating tests from text input."""
    code: str = Field(..., description="Source code as text", min_length=1, max_length=100000)
    language: Optional[LanguageEnum] = Field(None, description="Programming language (auto-detected if not provided)")
    
    @validator('code')
    def code_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Code cannot be empty')
        return v


class GitLabTestGenerationRequest(BaseModel):
    """Request model for generating tests from GitLab repository."""
    repo_url: str = Field(..., description="GitLab repository URL")
    access_token: Optional[str] = Field(None, description="GitLab access token for private repositories")
    branch: Optional[str] = Field("main", description="Branch name to analyze")
    max_files: Optional[int] = Field(50, description="Maximum number of files to process", ge=1, le=100)
    
    @validator('repo_url')
    def validate_gitlab_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Repository URL must start with http:// or https://')
        if 'gitlab' not in v.lower():
            raise ValueError('URL must be a GitLab repository')
        return v


# Response Models
class TestGenerationMetadata(BaseModel):
    """Metadata about the test generation process."""
    input_type: InputTypeEnum
    detected_language: Optional[str] = None
    test_framework: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    processing_time_ms: Optional[int] = None
    lines_of_code: Optional[int] = None
    files_processed: Optional[int] = None


class TestGenerationResponse(BaseModel):
    """Response model for successful test generation."""
    success: bool = True
    generated_tests: str = Field(..., description="Generated unit test code")
    metadata: TestGenerationMetadata
    coverage_notes: Optional[str] = None
    suggestions: Optional[List[str]] = None
    processing_messages: Optional[List[str]] = None


class TestGenerationErrorResponse(BaseModel):
    """Response model for failed test generation."""
    success: bool = False
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    processing_messages: Optional[List[str]] = None


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = "healthy"
    timestamp: str
    version: str
    dependencies: Dict[str, str]


class FileUploadResponse(BaseModel):
    """Response model for file upload validation."""
    filename: str
    size: int
    content_type: Optional[str] = None
    language_detected: Optional[str] = None
    valid: bool = True
    message: str = "File uploaded successfully"


# Error Models
class ValidationErrorDetail(BaseModel):
    """Detailed validation error information."""
    field: str
    message: str
    invalid_value: Any


class ErrorResponse(BaseModel):
    """Generic error response model."""
    error: str
    error_code: Optional[str] = None
    details: Optional[List[ValidationErrorDetail]] = None
    timestamp: str


# Configuration Models  
class APIConfig(BaseModel):
    """API configuration settings."""
    max_file_size: int = Field(10485760, description="Maximum file size in bytes (10MB)")
    supported_languages: List[str] = Field(default_factory=lambda: [
        "python", "java", "javascript", "typescript", "c#", "cpp", "c",
        "go", "rust", "php", "ruby", "swift", "kotlin", "scala"
    ])
    max_processing_time: int = Field(300, description="Maximum processing time in seconds")
    rate_limit_per_minute: int = Field(10, description="Rate limit per minute per client")
