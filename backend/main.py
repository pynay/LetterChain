from langgraph_flow import app_graph
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import PlainTextResponse


app = FastAPI()

@app.post("/generate", response_class=PlainTextResponse)
async def generate_cover_letter(
    resume: UploadFile,
    job: UploadFile,
    tone: str = Form("Emotionally intelligent, detailed, and clearly tailored to the role and mission. Shows initiative, reflection, and care — top-tier cover letter.")

): 
    resume_text = (await resume.read()).decode()
    job_text = (await job.read()).decode()


    state = {
        "resume_posting": resume_text,
        "job_posting": job_text,
        "tone": tone
    }

    result = app_graph.invoke(state)
    return result["cover_letter"]