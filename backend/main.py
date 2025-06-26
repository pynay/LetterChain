from langgraph_flow import app_graph, resume_parser_node, job_parser_node
from fastapi import FastAPI, UploadFile, Form, HTTPException, status, Request
from fastapi.responses import PlainTextResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import PyPDF2
import io
import json
import hashlib
import asyncio
import time
import random
import redis
import hashlib
import os

def make_resume_cache_key(resume_text: str) -> str:
    return "resume:" + hashlib.sha256(resume_text.encode()).hexdigest()


def make_job_cache_key(job_text: str) -> str:
    return "job:" + hashlib.sha256(job_text.encode()).hexdigest()




redis_client = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"),
                              decode_responses=True)
# Security constants
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
ALLOWED_MIME_TYPES = {"application/pdf", "text/plain"}

def validate_upload(file: UploadFile, file_bytes: bytes, file_label: str):
    """Validate file size, extension, and MIME type"""
    # Check file size
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"{file_label} file is too large (max 2MB)."
        )
    
    # Check extension
    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if f".{ext}" not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{file_label} file type not allowed. Only PDF and TXT are supported."
        )
    
    # Check MIME type (best effort, not bulletproof)
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{file_label} file MIME type not allowed."
        )

app = FastAPI()

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://letterchain05.vercel.app",
        "https://www.letterchain.fyi"
        ],  # or ["*"] for dev
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "LetterChain Backend is running"}

@app.post("/generate", response_class=PlainTextResponse)
@limiter.limit("5/minute")  # 5 requests per minute per IP
async def generate_cover_letter(
    request: Request,
    resume: UploadFile,
    job: UploadFile,
    tone: str = Form("Emotionally intelligent, detailed, and clearly tailored to the role and mission. Shows initiative, reflection, and care — top-tier cover letter.")
): 
    # Validate resume file
    resume_bytes = await resume.read()
    validate_upload(resume, resume_bytes, "Resume")
    
    resume_text = ""
    if resume.filename.lower().endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_bytes))
            resume_text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
        except Exception as e:
            return PlainTextResponse(f"Error reading PDF: {e}", status_code=400)
    else:
        resume_text = resume_bytes.decode(errors="ignore")

    # Validate job file
    job_bytes = await job.read()
    validate_upload(job, job_bytes, "Job description")
    job_text = job_bytes.decode(errors="ignore")

    resume_cache_key = make_resume_cache_key(resume_text)
    parsed_resume_json = redis_client.get(resume_cache_key)
    if parsed_resume_json:
        parsed_resume = json.loads(parsed_resume_json)
    else:
        resume_state = {"resume_posting": resume_text}
        parsed_resume_state = resume_parser_node(resume_state)
        parsed_resume = parsed_resume_state.get("resume_info", {})
        redis_client.set(resume_cache_key, json.dumps(parsed_resume), ex=86400)


    job_cache_key = make_job_cache_key(job_text)
    parsed_job_json = redis_client.get(job_cache_key)
    if parsed_job_json:
        parsed_job = json.loads(parsed_job_json)
    else:
        # Parse job and cache the result
        job_state = {"job_posting": job_text}
        parsed_job_state = job_parser_node(job_state)
        parsed_job = parsed_job_state.get("job_info", {})
        redis_client.set(job_cache_key, json.dumps(parsed_job), ex=86400)  # 24 hours

    state = {
        "resume_posting": resume_text,
        "job_posting": job_text,
        "tone": tone,
        "resume_info": parsed_resume,
        "job_info": parsed_job,
        "user_name": parsed_resume.get("name", "Candidate")
    }
    
    result = app_graph.invoke(state)
    if result.get("validation_failed"):
        error_details = result.get("validation_error", {})
        error_message = "Input validation failed:\n"
        if error_details.get("resume_issues"):
            error_message += f"Resume issues: {', '.join(error_details['resume_issues'])}\n"
        if error_details.get("job_issues"):
            error_message += f"Job description issues: {', '.join(error_details['job_issues'])}"
        return PlainTextResponse(error_message, status_code=400)
    return result["cover_letter"]

@app.post("/feedback")
@limiter.limit("10/minute")  # 10 requests per minute per IP (more lenient for feedback)
async def provide_feedback(
    request: Request,
    resume: UploadFile,
    job: UploadFile,
    tone: str = Form(),
    user_feedback: str = Form(),
    current_cover_letter: str = Form()
):
    # Validate resume file
    resume_bytes = await resume.read()
    validate_upload(resume, resume_bytes, "Resume")
    
    resume_text = ""
    if resume.filename.lower().endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_bytes))
            resume_text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading PDF: {e}")
    else:
        resume_text = resume_bytes.decode(errors="ignore")

    # Validate job file
    job_bytes = await job.read()
    validate_upload(job, job_bytes, "Job description")
    job_text = job_bytes.decode(errors="ignore")

    resume_cache_key = make_resume_cache_key(resume_text)
    parsed_resume_json = redis_client.get(resume_cache_key)
    if parsed_resume_json:
        parsed_resume = json.loads(parsed_resume_json)
    else:
        resume_state = {"resume_posting": resume_text}
        parsed_resume_state = resume_parser_node(resume_state)
        parsed_resume = parsed_resume_state.get("resume_info", {})
        redis_client.set(resume_cache_key, json.dumps(parsed_resume), ex=86400)

    job_cache_key = make_job_cache_key(job_text)
    parsed_job_json = redis_client.get(job_cache_key)
    if parsed_job_json:
        parsed_job = json.loads(parsed_job_json)
    else:
        job_state = {"job_posting": job_text}
        parsed_job_state = job_parser_node(job_state)
        parsed_job = parsed_job_state.get("job_info", {})
        redis_client.set(job_cache_key, json.dumps(parsed_job), ex=86400)
    # Create state with user feedback
    state = {
        "resume_posting": resume_text,
        "job_posting": job_text,
        "tone": tone,
        "resume_info": parsed_resume,
        "job_info": parsed_job,
        "user_name": parsed_resume.get("name", "Candidate"),
        "prior_issues": [user_feedback],  # Add user feedback as prior issues
        "cover_letter": current_cover_letter  # Include current cover letter for context
    }

    # Run the flow again with feedback
    result = app_graph.invoke(state)
    
    return JSONResponse({
        "cover_letter": result["cover_letter"],
        "validation_result": result.get("validation_result", {}),
        "message": "Cover letter regenerated with your feedback"
    })

@app.post("/generate-stream")
@limiter.limit("3/minute")  # 3 requests per minute per IP (more restrictive for streaming)
async def generate_cover_letter_stream(
    request: Request,
    resume: UploadFile,
    job: UploadFile,
    tone: str = Form("Emotionally intelligent, detailed, and clearly tailored to the role and mission. Shows initiative, reflection, and care — top-tier cover letter.")
):
    async def event_generator():
        try:
            # Step 1: Parse resume
            yield f"data: Parsing resume...\n\n"
            resume_bytes = await resume.read()
            validate_upload(resume, resume_bytes, "Resume")
            
            resume_text = ""
            if resume.filename.lower().endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_bytes))
                    resume_text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
                except Exception as e:
                    yield f"data: Error reading PDF: {e}\n\n"
                    return
            else:
                resume_text = resume_bytes.decode(errors="ignore")
            await asyncio.sleep(0.2)

            # Step 2: Parse job description
            yield f"data: Parsing job description...\n\n"
            job_bytes = await job.read()
            validate_upload(job, job_bytes, "Job description")
            job_text = job_bytes.decode(errors="ignore")
            await asyncio.sleep(0.2)


            resume_cache_key = make_resume_cache_key(resume_text)
            parsed_resume_json = redis_client.get(resume_cache_key)
            if parsed_resume_json:
                parsed_resume = json.loads(parsed_resume_json)
            else:
                resume_state = {"resume_posting": resume_text}
                parsed_resume_state = resume_parser_node(resume_state)
                parsed_resume = parsed_resume_state.get("resume_info", {})
                redis_client.set(resume_cache_key, json.dumps(parsed_resume), ex=86400)

            job_cache_key = make_job_cache_key(job_text)
            parsed_job_json = redis_client.get(job_cache_key)
            if parsed_job_json:
                parsed_job = json.loads(parsed_job_json)
            else:
                job_state = {"job_posting": job_text}
                parsed_job_state = job_parser_node(job_state)
                parsed_job = parsed_job_state.get("job_info", {})
                redis_client.set(job_cache_key, json.dumps(parsed_job), ex=86400)

            # Step 3: Matching experiences
            yield f"data: Matching experiences...\n\n"
            await asyncio.sleep(0.2)

            # Step 4: Generating cover letter
            yield f"data: Generating cover letter...\n\n"
            state = {
                "resume_posting": resume_text,
                "job_posting": job_text,
                "tone": tone,
                "resume_info": parsed_resume,
                "job_info": parsed_job,
                "user_name": parsed_resume.get("name", "Candidate")
            }
            
            try:
                result = app_graph.invoke(state)
            except Exception as e:
                # Check if it's an API overload error (529 status code)
                if "529" in str(e) or "overloaded" in str(e).lower():
                    yield f"data: ERROR::Anthropic API is currently overloaded. Please try again in a few moments.\n\n"
                elif "rate limit" in str(e).lower():
                    yield f"data: ERROR::Rate limit exceeded. Please wait a moment and try again.\n\n"
                else:
                    yield f"data: ERROR::An unexpected error occurred: {str(e)}\n\n"
                yield f"data: done\n\n"
                return
                
            await asyncio.sleep(0.2)

            # Check for validation errors
            if result.get("validation_failed"):
                error_details = result.get("validation_error", {})
                error_message = "Input validation failed:\n"
                if error_details.get("resume_issues"):
                    error_message += f"Resume issues: {', '.join(error_details['resume_issues'])}\n"
                if error_details.get("job_issues"):
                    error_message += f"Job description issues: {', '.join(error_details['job_issues'])}"
                yield f"data: ERROR::{error_message}\n\n"
                yield f"data: done\n\n"
                return

            # Step 5: Validating output
            yield f"data: Validating output...\n\n"
            await asyncio.sleep(0.2)

            # Final: Send cover letter
            yield f"data: FINAL_COVER_LETTER::{json.dumps({'cover_letter': result['cover_letter']})}\n\n"
            yield f"data: done\n\n"
            
        except Exception as e:
            yield f"data: ERROR::An unexpected error occurred: {str(e)}\n\n"
            yield f"data: done\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")