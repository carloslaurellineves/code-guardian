"""
GitLab API service for repository access and code extraction.
"""

import requests
from typing import List, Dict, Any, Optional
import logging
from urllib.parse import urlparse, quote
import base64

from src.config import config
from src.models import GitLabRepositoryInfo, FileInfo

logger = logging.getLogger(__name__)


class GitLabService:
    """Service for interacting with GitLab API to retrieve repository code."""

    def __init__(self, token: Optional[str] = None, base_url: str = None):
        """Initialize GitLab service with authentication token."""
        self.token = token or config.GITLAB_TOKEN
        self.base_url = base_url or config.GITLAB_URL
        self.api_base = f"{self.base_url}/api/v4"
        
        if not self.token:
            logger.warning("No GitLab token provided. Only public repositories will be accessible.")
        
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def extract_project_info(self, gitlab_url: str) -> GitLabRepositoryInfo:
        """Extract project information from GitLab URL."""
        try:
            parsed_url = urlparse(gitlab_url)
            path_parts = [part for part in parsed_url.path.split('/') if part]
            
            if len(path_parts) < 2:
                raise ValueError("Invalid GitLab URL format")
            
            # Extract namespace and project name
            namespace = path_parts[0]
            project_name = path_parts[1]
            
            # Remove .git suffix if present
            if project_name.endswith('.git'):
                project_name = project_name[:-4]
            
            project_path = f"{namespace}/{project_name}"
            
            return GitLabRepositoryInfo(
                url=gitlab_url,
                project_id=quote(project_path, safe=''),
                branch="main"  # Default branch, can be detected later
            )
            
        except Exception as e:
            logger.error(f"Failed to extract project info from URL {gitlab_url}: {e}")
            raise ValueError(f"Invalid GitLab URL: {e}")

    def get_project_details(self, project_id: str) -> Dict[str, Any]:
        """Get detailed information about a GitLab project."""
        try:
            url = f"{self.api_base}/projects/{project_id}"
            response = self.session.get(url)
            response.raise_for_status()
            
            project_data = response.json()
            logger.info(f"Retrieved project details for: {project_data.get('name', 'Unknown')}")
            
            return project_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get project details for {project_id}: {e}")
            raise

    def get_repository_tree(self, project_id: str, branch: str = "main", path: str = "") -> List[Dict[str, Any]]:
        """Get the repository file tree."""
        try:
            url = f"{self.api_base}/projects/{project_id}/repository/tree"
            params = {
                "ref": branch,
                "path": path,
                "recursive": True,
                "per_page": 100
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            tree_data = response.json()
            logger.info(f"Retrieved {len(tree_data)} items from repository tree")
            
            return tree_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get repository tree for {project_id}: {e}")
            raise

    def get_file_content(self, project_id: str, file_path: str, branch: str = "main") -> str:
        """Get the content of a specific file from the repository."""
        try:
            url = f"{self.api_base}/projects/{project_id}/repository/files/{quote(file_path, safe='')}/raw"
            params = {"ref": branch}
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # GitLab API returns raw file content
            content = response.text
            logger.info(f"Retrieved content for file: {file_path} ({len(content)} characters)")
            
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get file content for {file_path}: {e}")
            raise

    def filter_source_files(self, tree_items: List[Dict[str, Any]]) -> List[str]:
        """Filter tree items to get only source code files."""
        source_extensions = {
            '.py', '.java', '.js', '.ts', '.jsx', '.tsx', '.cs', '.cpp', '.c', '.h',
            '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala', '.m', '.mm',
            '.pl', '.sh', '.ps1', '.r', '.dart', '.lua', '.clj', '.fs', '.ml'
        }
        
        source_files = []
        
        for item in tree_items:
            if item.get('type') == 'blob':  # Regular file
                file_path = item.get('path', '')
                file_name = item.get('name', '')
                
                # Check file extension
                for ext in source_extensions:
                    if file_name.lower().endswith(ext):
                        source_files.append(file_path)
                        break
        
        logger.info(f"Found {len(source_files)} source code files")
        return source_files

    def get_repository_source_code(self, gitlab_url: str, max_files: int = 50) -> Dict[str, Any]:
        """
        Get source code from a GitLab repository.
        
        Args:
            gitlab_url: URL of the GitLab repository
            max_files: Maximum number of files to process
            
        Returns:
            Dictionary containing combined source code and metadata
        """
        try:
            # Extract project information
            repo_info = self.extract_project_info(gitlab_url)
            
            # Get project details to determine default branch
            project_details = self.get_project_details(repo_info.project_id)
            default_branch = project_details.get('default_branch', 'main')
            repo_info.branch = default_branch
            
            # Detect primary language
            repo_info.primary_language = project_details.get('language')
            
            # Get repository tree
            tree_items = self.get_repository_tree(repo_info.project_id, default_branch)
            
            # Filter to source files only
            source_files = self.filter_source_files(tree_items)
            
            # Limit the number of files to process
            if len(source_files) > max_files:
                logger.warning(f"Repository has {len(source_files)} source files. Limiting to {max_files}.")
                source_files = source_files[:max_files]
            
            # Retrieve file contents
            files_content = []
            combined_code = []
            
            for file_path in source_files:
                try:
                    content = self.get_file_content(repo_info.project_id, file_path, default_branch)
                    
                    file_info = FileInfo(
                        path=file_path,
                        content=content,
                        size=len(content)
                    )
                    
                    files_content.append(file_info)
                    
                    # Add to combined code with file separator
                    combined_code.append(f"\n# ===== File: {file_path} =====\n")
                    combined_code.append(content)
                    
                except Exception as e:
                    logger.warning(f"Failed to get content for {file_path}: {e}")
                    continue
            
            repo_info.files = [f.path for f in files_content]
            
            result = {
                "repository_info": repo_info,
                "files": files_content,
                "combined_code": "\n".join(combined_code),
                "total_files": len(files_content),
                "total_size": sum(f.size for f in files_content)
            }
            
            logger.info(f"Successfully retrieved {len(files_content)} files from repository")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get repository source code: {e}")
            raise

    def detect_primary_language(self, files: List[FileInfo]) -> str:
        """Detect the primary programming language of the repository."""
        language_extensions = {
            '.py': 'python',
            '.java': 'java',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.cs': 'c#',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala'
        }
        
        language_counts = {}
        
        for file_info in files:
            for ext, lang in language_extensions.items():
                if file_info.path.lower().endswith(ext):
                    language_counts[lang] = language_counts.get(lang, 0) + 1
                    break
        
        if language_counts:
            primary_language = max(language_counts, key=language_counts.get)
            logger.info(f"Detected primary language: {primary_language} ({language_counts[primary_language]} files)")
            return primary_language
        
        return "unknown"

    def test_connection(self) -> bool:
        """Test the GitLab API connection."""
        try:
            url = f"{self.api_base}/user" if self.token else f"{self.api_base}/version"
            response = self.session.get(url)
            response.raise_for_status()
            
            logger.info("GitLab API connection successful")
            return True
            
        except Exception as e:
            logger.error(f"GitLab API connection failed: {e}")
            return False
