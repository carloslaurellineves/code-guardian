"""
API router for file upload endpoints.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
import os
import tempfile
import aiofiles
from typing import Optional

from api.schemas import (
    FileUploadResponse,
    TestGenerationResponse, 
    TestGenerationErrorResponse,
    TestGenerationMetadata,
    InputTypeEnum
)
from api.services.file_service import FileService
from api.services.orchestrator_service import OrchestratorService
from src.config import config

logger = logging.getLogger(__name__)
router = APIRouter()


# Dependencies
def get_file_service() -> FileService:
    """Dependency to provide file service."""
    return FileService()


def get_orchestrator_service() -> OrchestratorService:
    """Dependency to provide orchestrator service."""
    return OrchestratorService()


@router.post(
    "/validate",
    response_model=FileUploadResponse,
    summary="Validate uploaded file",
    description="Validate an uploaded file for test generation compatibility"
)
async def validate_file(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service)
):
    """Validate uploaded file without generating tests."""
    try:
        logger.info(f"Validating uploaded file: {file.filename}")
        
        # Validate file
        validation_result = await file_service.validate_file(file)
        
        if validation_result["valid"]:
            response = FileUploadResponse(
                filename=file.filename,
                size=validation_result["size"],
                content_type=file.content_type,
                language_detected=validation_result.get("language"),
                valid=True,
                message="File is valid for test generation"
            )
            logger.info(f"File validation successful: {file.filename}")
            return response
        else:
            response = FileUploadResponse(
                filename=file.filename,
                size=validation_result["size"],
                content_type=file.content_type,
                valid=False,
                message=validation_result.get("error", "File validation failed")
            )
            logger.warning(f"File validation failed: {file.filename} - {validation_result.get('error')}")
            return JSONResponse(status_code=400, content=response.dict())
            
    except Exception as e:
        logger.error(f"Error validating file {file.filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File validation error: {str(e)}"
        )


@router.post(
    "/generate-tests",
    response_model=TestGenerationResponse,
    responses={
        400: {"model": TestGenerationErrorResponse},
        422: {"model": TestGenerationErrorResponse},
        500: {"model": TestGenerationErrorResponse}
    },
    summary="Generate tests from uploaded file",
    description="Upload a source code file and generate unit tests for it"
)
async def generate_tests_from_file(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    file_service: FileService = Depends(get_file_service),
    orchestrator_service: OrchestratorService = Depends(get_orchestrator_service)
):
    """Generate unit tests from uploaded file."""
    temp_file_path = None
    
    try:
        logger.info(f"Generating tests from uploaded file: {file.filename}")
        
        # Validate file first
        validation_result = await file_service.validate_file(file)
        if not validation_result["valid"]:
            error_response = TestGenerationErrorResponse(
                success=False,
                error=validation_result.get("error", "File validation failed"),
                error_code="FILE_VALIDATION_FAILED"
            )
            return JSONResponse(status_code=400, content=error_response.dict())
        
        # Save file temporarily
        temp_file_path = await file_service.save_temp_file(file)
        
        # Use orchestrator service to generate tests
        result = await orchestrator_service.generate_from_file(
            file_path=temp_file_path,
            language=language or validation_result.get("language")
        )
        
        # Build metadata
        metadata = TestGenerationMetadata(
            input_type=InputTypeEnum.FILE,
            detected_language=result.get("detected_language"),
            test_framework=result.get("test_framework"),
            files_processed=1
        )
        
        if result.get("success"):
            response = TestGenerationResponse(
                success=True,
                generated_tests=result.get("generated_tests", ""),
                metadata=metadata,
                coverage_notes=result.get("coverage_notes"),
                suggestions=result.get("suggestions", []),
                processing_messages=result.get("processing_messages", [])
            )
            logger.info(f"Successfully generated tests from file: {file.filename}")
            return response
        else:
            error_response = TestGenerationErrorResponse(
                success=False,
                error=result.get("error", "Unknown error occurred"),
                error_code="FILE_GENERATION_FAILED",
                processing_messages=result.get("processing_messages", [])
            )
            logger.error(f"File test generation failed: {result.get('error')}")
            return JSONResponse(status_code=400, content=error_response.dict())
            
    except Exception as e:
        logger.error(f"Unexpected error in generate_tests_from_file: {e}", exc_info=True)
        error_response = TestGenerationErrorResponse(
            success=False,
            error=str(e),
            error_code="INTERNAL_ERROR"
        )
        return JSONResponse(status_code=500, content=error_response.dict())
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")
