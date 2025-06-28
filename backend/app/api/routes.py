from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse, JSONResponse
from typing import Optional
import logging
from datetime import datetime
from app.core.tracing import tracing_service
from app.services.graph_service import GraphService
from app.services.file_service import file_service
from app.services.cache_service import cache_service
from app.models.schemas import (
    CoverLetterRequest, CoverLetterResponse, FeedbackRequest,
    ValidationResult, ErrorResponse, ToneEnum
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate", response_model=CoverLetterResponse)
@tracing_service.trace_api_request("generate_cover_letter")
async def generate_cover_letter(
    resume: UploadFile,
    job: UploadFile,
    tone: ToneEnum = Form(ToneEnum.PROFESSIONAL),
    graph_service: GraphService = Depends()
):
    """
    Generate a cover letter from uploaded resume and job description.
    
    This endpoint:
    1. Validates uploaded files
    2. Extracts text content
    3. Checks cache for parsed data
    4. Runs the LangGraph workflow
    5. Returns the generated cover letter with metadata
    """

    try: 
        resume_bytes = await resume.read()
        resume_validation = file_service.validate_upload(resume, resume_bytes, "Resume")
        if not resume_validation.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=resume_validation.error_message
            )
        job_bytes = await job.read()
        job_validation = file_service.validate_upload(job, job_bytes, "Job description")
        if not job_validation.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=job_validation.error_message
            )
        
        resume_text = file_service.extract_text(resume, resume_bytes)
        job_text = file_service.extract_text(job, job_bytes)

        parsed_resume = cache_service.get_parsed_resume(resume_text)
        if not parsed_resume:
            logger.info("Resume not found in cache, will parse")

        parsed_job = cache_service.get_parsed_job(job_text)
        if not parsed_job:
            logger.info("Job not found in cache, will parse")
        
        state = {
            "resume_posting": resume_text,
            "job_posting": job_text,
            "tone": tone.value,
             "resume_info": parsed_resume or {},
            "job_info": parsed_job or {}
        }

        result = await graph_service.invoke_graph(state)


        if "error" in result:
            error_detail = result["error"].get("details", "Unknown error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Cover letter generation failed: {error_detail}"
            )
        
        if result.get("validation_failed"):
            validation_error = result.get("validation_error", {})
            error_message = "Input validation failed\n"
            if validation_error.get("resume_issues"):
                error_message += f"Resume issues: {', '.join(validation_error['resume_issues'])}\n"
            if validation_error.get("job_issues"):
                error_message += f"Job description issues: {', '.join(validation_error['job_issues'])}"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        # Cache parsed data if not already cached
        if not parsed_resume and "resume_info" in result:
            cache_service.set_parsed_resume(resume_text, result["resume_info"])
        
        if not parsed_job and "job_info" in result:
            cache_service.set_parsed_job(job_text, result["job_info"])
        
        # Build response
        response = CoverLetterResponse(
            cover_letter=result["cover_letter"],
            job_info=result["job_info"],
            resume_info=result["resume_info"],
            matched_experiences=result.get("matched_experiences", []),
            generation_metadata=result.get("generation_metadata", {})
        )
        
        logger.info("Cover letter generated successfully", 
                   extra={"user_name": result.get("user_name"), "job_title": result["job_info"].get("title")})
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_cover_letter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/generate-stream")
@tracing_service.trace_api_request("generate_cover_letter_stream")
async def generate_cover_letter_stream(
    resume: UploadFile,
    job: UploadFile,
    tone: ToneEnum = Form(ToneEnum.PROFESSIONAL),
    graph_service: GraphService = Depends()
):
    """
    Generate cover letter with streaming response for real-time updates.
    
    This endpoint provides streaming updates as the workflow progresses,
    useful for showing progress to users during generation.
    """
    from fastapi.responses import StreamingResponse
    import json

    async def event_generator():
        try:
            # File validation (same as non-streaming endpoint)
            resume_bytes = await resume.read()
            resume_validation = file_service.validate_upload(resume, resume_bytes, "Resume")
            if not resume_validation.is_valid:
                yield f"data: {json.dumps({'error': resume_validation.error_message})}\n\n"
                return
            job_bytes = await job.read()
            job_validation = file_service.validate_upload(job, job_bytes, "Job description")
            if not job_validation.is_valid:
                yield f"data: {json.dumps({'error': job_validation.error_message})}\n\n"
                return
            # Extract text
            resume_text = file_service.extract_text(resume, resume_bytes)
            job_text = file_service.extract_text(job, job_bytes)
            # Stream workflow progress
            state = {
                "resume_posting": resume_text,
                "job_posting": job_text,
                "tone": tone.value
            }
            # Execute workflow with streaming updates
            async for message in graph_service.invoke_graph_streaming(state):
                yield message
        except Exception as e:
            logger.error(f"Streaming generation failed: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@router.post("/feedback")
@tracing_service.trace_api_request("provide_feedback")
async def provide_feedback(
    request: FeedbackRequest,
    graph_service: GraphService = Depends()
):
    """
    Provide feedback on a generated cover letter to improve future generations.
    
    This endpoint allows users to provide feedback on generated cover letters,
    which can be used to improve the AI models and workflow.
    """
    
    try:
        # Create state with feedback
        state = {
            "resume_posting": request.resume_text,
            "job_posting": request.job_text,
            "tone": request.tone.value,
            "cover_letter": request.cover_letter,
            "user_feedback": request.user_feedback,
            "feedback_mode": True
        }
        
        # Execute workflow with feedback
        result = await graph_service.invoke_graph_with_feedback(state)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"].get("details", "Feedback processing failed")
            )
        
        return {
            "message": "Feedback processed successfully",
            "improved_letter": result.get("cover_letter"),
            "feedback_analysis": result.get("feedback_analysis", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Feedback processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": str(datetime.utcnow()),
        "version": "1.0.0"
    }

@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics for monitoring"""
    try:
        stats = cache_service.get_cache_stats()
        return {"cache_stats": stats}
    except Exception as e:
        logger.error(f"Failed to get cache stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cache statistics"
        )
        



