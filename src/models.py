"""
Data models for the Code Guardian application.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from langchain_core.messages import BaseMessage


class InputType(Enum):
    """Enumeration of supported input types."""
    TEXT = "text"
    FILE = "file"
    GITLAB = "gitlab"


@dataclass
class ProcessingState:
    """State object that flows through the LangGraph workflow."""
    
    # Input information
    input_type: InputType
    text_input: Optional[str] = None
    file_path: Optional[str] = None
    gitlab_url: Optional[str] = None
    
    # Processing state
    is_valid: bool = False
    processed_code: Optional[str] = None
    detected_language: Optional[str] = None
    
    # Generated content
    generated_tests: Optional[str] = None
    test_framework: Optional[str] = None
    coverage_notes: Optional[str] = None
    
    # Output and errors
    final_output: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    # Messages for workflow tracking
    messages: List[BaseMessage] = field(default_factory=list)


@dataclass
class TestGenerationResult:
    """Result object for test generation."""
    
    test_code: str
    framework: str
    coverage_notes: str
    language: str
    confidence_score: float = 0.0
    suggestions: List[str] = field(default_factory=list)


@dataclass
class GitLabRepositoryInfo:
    """Information about a GitLab repository."""
    
    url: str
    project_id: Optional[str] = None
    branch: str = "main"
    files: List[str] = field(default_factory=list)
    primary_language: Optional[str] = None


@dataclass
class FileInfo:
    """Information about a processed file."""
    
    path: str
    content: str
    language: Optional[str] = None
    size: int = 0
    encoding: str = "utf-8"
