"""
File service utilities for file handling in the API.
"""

import os
import tempfile
import aiofiles
import logging
from fastapi import UploadFile
from typing import Dict
from src.config import config


logger = logging.getLogger(__name__)


class FileService:
    """Service utilities for handling file uploads."""
    
    async def validate_file(self, file: UploadFile) -> Dict[str, any]:
        """
        Validate the uploaded file is of a supported type and within the size limit.
        
        Args:
            file (UploadFile): UploadFile class instance
        
        Returns:
            dict: Dictionary containing validation result
        """
        logger.info(f"Validating file {file.filename}")
        
        # Get file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        # Check against the maximum file size
        if file_size > config.MAX_FILE_SIZE:
            logger.warning(f"File {file.filename} exceeds max file size limit")
            return {"valid": False, "size": file_size, "error": "File exceeds maximum allowed size"}
        
        # Detect language by file extension
        language = self._detect_language_by_extension(file.filename)
        if language == "unknown":
            logger.warning(f"Unsupported file type for file {file.filename}")
            return {"valid": False, "size": file_size, "error": "Unsupported file type"}
        
        return {"valid": True, "size": file_size, "language": language}
    
    
    def _detect_language_by_extension(self, filename: str) -> str:
        """
        Detect programming language based on the file extension.
        
        Args:
            filename (str): Filename to determine language
        
        Returns:
            str: Detected language name
        """
        extension_to_language = {
            ".py": "python",
            ".java": "java",
            ".js": "javascript",
            ".ts": "typescript",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "c#",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala"
        }
        _, ext = os.path.splitext(filename)
        return extension_to_language.get(ext.lower(), "unknown")

    
    async def save_temp_file(self, file: UploadFile) -> str:
        """
        Save an uploaded file temporarily.
        
        Args:
            file (UploadFile): UploadFile class instance

        Returns:
            path: Path to the saved temporary file
        """
        logger.info(f"Saving temporary file for {file.filename}")
        
        # Create temp file path
        temp_file_path = os.path.join(tempfile.gettempdir(), file.filename)
        
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write

        logger.info(f"Temporary file saved: {temp_file_path}")
        return temp_file_path

