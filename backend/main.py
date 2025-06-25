from langgraph_flow import app_graph
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import io
import json
import hashlib
import asyncio




app = FastAPI()
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

    state = {
        "resume_posting": resume_text,
        "job_posting": job_text,
        "tone": tone
    }

    if (len(state["resume_posting"]) < 150 or len(state["job_posting"] < 150)): 
         error_message = "Input validation failed:\n"
         return PlainTextResponse(error_message, status_code=400)
    
    
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

@app.post("/generate-stream")
async def generate_cover_letter_stream(
    resume: UploadFile,
    job: UploadFile,
    tone: str = Form("Emotionally intelligent, detailed, and clearly tailored to the role and mission. Shows initiative, reflection, and care — top-tier cover letter.")
):
    async def event_generator():
        # Step 1: Parse resume
        yield f"data: Parsing resume...\n\n"
        resume_bytes = await resume.read()
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
        job_text = (await job.read()).decode(errors="ignore")
        await asyncio.sleep(0.2)

        # Step 3: Matching experiences
        yield f"data: Matching experiences...\n\n"
        await asyncio.sleep(0.2)

        # Step 4: Generating cover letter
        yield f"data: Generating cover letter...\n\n"
        state = {
            "resume_posting": resume_text,
            "job_posting": job_text,
            "tone": tone
        }
        result = app_graph.invoke(state)
        await asyncio.sleep(0.2)

        # Step 5: Validating output
        yield f"data: Validating output...\n\n"
        await asyncio.sleep(0.2)

        # Final: Send cover letter
        yield f"data: FINAL_COVER_LETTER::{json.dumps({'cover_letter': result['cover_letter']})}\n\n"
        yield f"data: done\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")