"""
Handler module to manage input types for unit test generation.
"""

from src.llm_calls import OpenAIClient
from src.models import GitLabRepositoryInfo, FileInfo
from src.services import GitLabService
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)


class TextHandler:
    """Handle text input processing."""

    def __init__(self):
        self.llm_client = OpenAIClient()

    def process(self, source_code_text: str) -> str:
        """Process source code from text input."""
        return self.llm_client.generate_tests(source_code_text)

    def detect_language(self, code: str) -> str:
        """Detect the programming language of the provided code."""
        # Dummy logic for language detection
        return "python"


class FileHandler:
    """Handle file upload processing."""

    def __init__(self):
        self.llm_client = OpenAIClient()

    def process(self, file_path: str) -> str:
        """Process source code from file input."""
        with open(file_path, 'r', encoding='utf-8') as file:
            code_content = file.read()
        return self.llm_client.generate_tests(code_content)

    def detect_language_from_file(self, file_path: str) -> str:
        """Detect the programming language from the file extension or content."""
        _, ext = os.path.splitext(file_path)
        # Dummy logic for detecting language
        ext_to_language = {
            ".py": "python",
            ".java": "java",
            ".js": "javascript",
            # Extend with more mappings as needed
        }
        return ext_to_language.get(ext, "unknown")


class GitLabHandler:
    """Handle GitLab repository input processing."""

    def __init__(self):
        self.gitlab_service = GitLabService()

    def process(self, gitlab_url: str) -> str:
        """Retrieve code from a GitLab repository and combine for processing."""
        try:
            logger.info(f"Processing GitLab repository: {gitlab_url}")
            
            # Get repository source code using GitLab service
            repo_data = self.gitlab_service.get_repository_source_code(gitlab_url)
            
            # Return combined code for test generation
            return repo_data["combined_code"]
            
        except Exception as e:
            logger.error(f"Failed to process GitLab repository {gitlab_url}: {e}")
            # Return a placeholder if GitLab processing fails
            return f"# Error processing GitLab repository: {e}\n# URL: {gitlab_url}"

    def detect_primary_language(self, code: str) -> str:
        """Detect the primary programming language of the repository."""
        try:
            # Try to extract language from the processed code structure
            # This is a simplified detection based on file extensions in comments
            if ".py" in code:
                return "python"
            elif ".java" in code:
                return "java"
            elif ".js" in code or ".jsx" in code:
                return "javascript"
            elif ".ts" in code or ".tsx" in code:
                return "typescript"
            elif ".cs" in code:
                return "c#"
            elif ".go" in code:
                return "go"
            else:
                return "unknown"
                
        except Exception as e:
            logger.warning(f"Failed to detect primary language: {e}")
            return "unknown"
