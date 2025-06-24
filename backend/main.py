from langgraph_flow import app_graph
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import io




app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for dev
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

    result = app_graph.invoke(state)
    return result["cover_letter"]