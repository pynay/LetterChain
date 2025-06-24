from langgraph_flow import app_graph
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import io
import json
import hashlib
import redis




app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for dev
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Redis (default localhost:6379, db 0)
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def make_cache_key(resume_text, job_text, tone):
    m = hashlib.sha256()
    m.update(resume_text.encode("utf-8"))
    m.update(job_text.encode("utf-8"))
    m.update(tone.encode("utf-8"))
    return m.hexdigest()

@app.post("/generate", response_class=PlainTextResponse)
async def generate_cover_letter(
    resume: UploadFile,
    job: UploadFile,
    tone: str = Form("Emotionally intelligent, detailed, and clearly tailored to the role and mission. Shows initiative, reflection, and care — top-tier cover letter.")

): 
    # Handle resume file (PDF or TXT)
    resume_bytes = await resume.read()
    resume_text = ""
    if resume.filename.lower().endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_bytes))
            resume_text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
        except Exception as e:
            return PlainTextResponse(f"Error reading PDF: {e}", status_code=400)
    else:
        resume_text = resume_bytes.decode(errors="ignore")

    # Handle job file (assume TXT)
    job_text = (await job.read()).decode(errors="ignore")

    # Redis cache lookup
    cache_key = make_cache_key(resume_text, job_text, tone)
    cached = redis_client.get(cache_key)
    if cached:
        return cached

    state = {
        "resume_posting": resume_text,
        "job_posting": job_text,
        "tone": tone
    }

    result = app_graph.invoke(state)
    cover_letter = result["cover_letter"]
    redis_client.set(cache_key, cover_letter, ex=60*60*24*7)  # 7 days expiry
    return cover_letter

@app.post("/feedback")
async def provide_feedback(
    resume: UploadFile,
    job: UploadFile,
    tone: str = Form(),
    user_feedback: str = Form(),
    current_cover_letter: str = Form()
):
    # Handle resume file (PDF or TXT)
    resume_bytes = await resume.read()
    resume_text = ""
    if resume.filename.lower().endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_bytes))
            resume_text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading PDF: {e}")
    else:
        resume_text = resume_bytes.decode(errors="ignore")

    # Handle job file (assume TXT)
    job_text = (await job.read()).decode(errors="ignore")

    # Create state with user feedback
    state = {
        "resume_posting": resume_text,
        "job_posting": job_text,
        "tone": tone,
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