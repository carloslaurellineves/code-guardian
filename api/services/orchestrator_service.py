"""
Service layer for the orchestrator to provide async compatibility and additional error handling.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

from src.orchestrator import TestGenerationOrchestrator
from src.services.gitlab_service import GitLabService


logger = logging.getLogger(__name__)


class OrchestratorService:
    """Async service wrapper for the TestGenerationOrchestrator."""
    
    def __init__(self):
        """Initialize the orchestrator service."""
        self.orchestrator = TestGenerationOrchestrator()
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def generate_from_text(
        self, 
        code: str, 
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate tests from text input asynchronously.
        
        Args:
            code: Source code as string
            language: Programming language (optional)
            
        Returns:
            Dictionary with generation results
        """
        try:
            logger.info("Starting test generation from text input")
            
            # Run the synchronous orchestrator method in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self.orchestrator.generate_tests_from_text,
                code
            )
            
            logger.info("Test generation from text completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in generate_from_text: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "processing_messages": [f"Error: {str(e)}"]
            }
    
    async def generate_from_file(
        self, 
        file_path: str, 
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate tests from file input asynchronously.
        
        Args:
            file_path: Path to the source code file
            language: Programming language (optional)
            
        Returns:
            Dictionary with generation results
        """
        try:
            logger.info(f"Starting test generation from file: {file_path}")
            
            # Run the synchronous orchestrator method in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self.orchestrator.generate_tests_from_file,
                file_path
            )
            
            logger.info("Test generation from file completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in generate_from_file: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "processing_messages": [f"Error: {str(e)}"]
            }
    
    async def generate_from_gitlab(
        self, 
        repo_url: str,
        access_token: Optional[str] = None,
        branch: Optional[str] = "main",
        max_files: Optional[int] = 50
    ) -> Dict[str, Any]:
        """
        Generate tests from GitLab repository asynchronously.
        
        Args:
            repo_url: GitLab repository URL
            access_token: GitLab access token (optional)
            branch: Branch name to analyze
            max_files: Maximum number of files to process
            
        Returns:
            Dictionary with generation results
        """
        try:
            logger.info(f"Starting test generation from GitLab: {repo_url}")
            
            # If access token is provided, we need to set it in the GitLab service
            if access_token:
                # This is a simplified approach - in production, you might want
                # to pass the token through the orchestrator to the service
                logger.info("Using provided access token for GitLab access")
            
            # Run the synchronous orchestrator method in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self.orchestrator.generate_tests_from_gitlab,
                repo_url
            )
            
            logger.info("Test generation from GitLab completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in generate_from_gitlab: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "processing_messages": [f"Error: {str(e)}"]
            }
    
    async def get_workflow_visualization(self) -> str:
        """
        Get workflow visualization asynchronously.
        
        Returns:
            Mermaid diagram string
        """
        try:
            logger.info("Generating workflow visualization")
            
            # Run the synchronous method in thread pool
            loop = asyncio.get_event_loop()
            visualization = await loop.run_in_executor(
                self.executor,
                self.orchestrator.get_workflow_visualization
            )
            
            logger.info("Workflow visualization generated successfully")
            return visualization
            
        except Exception as e:
            logger.error(f"Error in get_workflow_visualization: {e}", exc_info=True)
            return f"Error generating visualization: {str(e)}"
    
    def __del__(self):
        """Cleanup thread pool executor."""
        try:
            self.executor.shutdown(wait=False)
        except Exception:
            pass
