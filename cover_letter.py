import os
import argparse
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph
import json
from typing import TypedDict, List, Optional
import re
from dotenv import load_dotenv
load_dotenv()
print("hi")
#setting up claude client
api_key = os.getenv("ANTHROPIC_API_KEY")

class CoverLetterState(TypedDict, total=False):
    job_posting: str
    resume_posting: str
    tone: str
    job_info: dict
    resume_info: dict
    matched_experiences: List[dict]
    cover_letter: str
    validation_result: dict
    prior_issues: Optional[List[str]]
    export_path: Optional[str]
    user_name: Optional[str]

claude = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    anthropic_api_key=api_key
)

#parser logic/parsing for job/resume text and tone
parser = argparse.ArgumentParser(description="Your script description")
parser.add_argument("--resume", type=str, required=True, help="Path to resume file")
parser.add_argument("--job", type=str, required=True, help="Path to the job description file")
parser.add_argument("--tone", type=str, default="formal", help="Tone of the cover letter")

args = parser.parse_args()

with open(args.resume, "r") as f:
    resume_text = f.read()

with open(args.job, "r") as f:
    job_text = f.read()

tone = args.tone

graph = StateGraph(CoverLetterState)

initial_state = {
    "job_posting": job_text, 
    "resume_posting": resume_text,
    "tone": tone
}

def extract_json_from_markdown(text):
    match = re.search(r"```(?:json)?\\n?(.*)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

#DEFINING ALL THE NODES FOR LANGGRAPH
def job_parser_node(state: dict) -> dict:
    job_posting = state["job_posting"]
    prompt = f"""
You are an intelligent assistant helping generate personalized cover letters by extracting structured information from job postings.

Please read the job description below and return a JSON object with the following fields:

- "title"
- "company"
- "required_skills" (list)
- "tone" (choose from: formal, casual, enthusiastic, corporate, technical)
- "values" (list)
- "summary" (2–3 sentences)

Return ONLY the JSON object. Do not include triple backticks or any text before or after the JSON.

### Job Description:
{job_posting}
"""
    response = claude.invoke(prompt)
    content = extract_json_from_markdown(response.content)
    print("Claude raw response in job_parser_node:", repr(content))
    if not content:
        print("Claude returned empty response in job_parser_node.")
        state["job_info"] = {}
        return state
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        print("Claude returned invalid JSON in job_parser_node:", content)
        state["job_info"] = {}
        return state
    state["job_info"] = parsed
    return state


def resume_parser_node(state: dict) -> dict:
    resume_text = state["resume_posting"]

    prompt = f"""
You are an intelligent assistant that extracts personal information from a candidate's resume to help make personalized cover letters.

Your task is to read the resume below and return a JSON object with the following fields:

- "name": The candidate's full name, if present.
- "summary": A 2–3 sentence overview of the candidate's background.
- "experiences": A list of up to 5 relevant work experiences or projects. Each should include:
    - "title": Role or position
    - "organization": Company or institution
    - "description": 1–2 sentence summary of what the person did
    - "skills_used": List of technical or domain-specific skills used in that experience
- "skills": A deduplicated list of skills explicitly or implicitly mentioned (e.g., Python, SQL, tutoring, machine learning, communication).
- "education": A list of schools or degrees, including:
    - "institution"
    - "degree"
    - "field"
    - "graduation_year" (if available)

Only extract what's present in the text - do not guess or hallucinate. Return ONLY the JSON object. Return ONLY the JSON object. Do not include triple backticks or any text before or after the JSON.

### Resume:
{resume_text}
"""

    response = claude.invoke(prompt)
    content = extract_json_from_markdown(response.content)
    try:
        parsed = json.loads(content)
        state["resume_info"] = parsed
    except json.JSONDecodeError:
        print("Claude returned invalid JSON for resume. Response:", content)
        state["resume_info"] = {}  # Or handle as appropriate

    return state


def relevance_matcher_node(state: dict) -> dict:
    resume_info = state.get("resume_info")
    job_info = state.get("job_info")
    if not resume_info or not job_info:
        print("Missing resume_info or job_info, skipping relevance matching.")
        state["matched_experiences"] = []
        return state

    prompt = f"""
You are an assistant that compares a candidate's resume to a job description and identifies the most relevant experiences for tailoring a personalized cover letter.

Please return a JSON object with the following fields:

- "matched_experiences": A list of the 2–3 most relevant experiences from the resume that match the job. Each item should include:
    - "title": The candidate's role
    - "organization": Company or project name
    - "reason": Why this experience is a strong match for the job

Only use experiences actually listed in the resume. Do not invent any content. Return ONLY the JSON object. Do not include triple backticks or any text before or after the JSON.

### Resume Data:
{resume_info}

### Job Description:
{job_info}
"""
    
    response = claude.invoke(prompt)
    content = extract_json_from_markdown(response.content)
    try:
        print("Claude response in relevance_matcher_node:", content)
        parsed = json.loads(content)
        state["matched_experiences"] = parsed.get("matched_experiences", [])
    except json.JSONDecodeError:
        print("Invalid JSON from Claude in relevance_matcher_node:", content)
        state["matched_experiences"] = []
    return state


def cover_letter_generator_node(state: dict) -> dict:
    job = state["job_info"]
    experiences = state["matched_experiences"]
    user_name = state.get("user_name", "Candidate")  # Optional fallback
    tone = job.get("tone", "formal")
    prior_issues = state.get("prior_issues", [])

    prompt = f"""
You are a helpful assistant that writes personalized cover letters based on structured resume and job data.

Write a one-page cover letter that:
- Addresses the company and job title directly
- Highlights 2–3 relevant experiences from the candidate
- Uses a {tone} tone
- Is specific, concise, and professional

Include the candidate's name at the end (e.g., "Sincerely, {user_name}").

Use only the experiences and job information provided — do not invent content.

### Job Information:
{job}

### Relevant Experiences:
{experiences}
"""

    if prior_issues:
        issue_str = "\n".join(f"- {issue}" for issue in prior_issues)
        prompt += f"""

The previous draft of this letter was rejected for the following reasons. Please address them:
{issue_str}
"""

    response = claude.invoke(prompt)
    state["cover_letter"] = response.content
    return state


def cover_letter_validator_node(state: dict) -> dict:
    letter = state["cover_letter"]
    job = state["job_info"]
    tone = job.get("tone", "formal")

    prompt = f"""
You are a quality assurance assistant for AI-generated cover letters.

Evaluate the following cover letter based on these criteria:
1. Does it mention the company name and job title?
2. Does it highlight at least two experiences that are relevant to the job?
3. Does it match the required tone ("{tone}")?
4. Is it specific and non-generic?
5. Is it under one page (approx. 400–500 words)?

Return a JSON object with:
- "valid": true or false
- "issues": list of strings describing problems if any are found

Only return the JSON object. Do not add commentary. Do not include triple backticks or any text before or after the JSON.

### Cover Letter:
{letter}

### Job Info:
{job}
"""

    response = claude.invoke(prompt)
    content = extract_json_from_markdown(response.content)
    try:
        validation_result = json.loads(content)
        state["validation_result"] = validation_result
        if not validation_result["valid"]:
            state["prior_issues"] = validation_result["issues"]
    except json.JSONDecodeError:
        print("Invalid JSON from Claude in cover_letter_validator_node:", content)
        state["validation_result"] = {"valid": False, "issues": ["Claude returned invalid JSON"]}
    return state

def exporter_node(state: dict) -> dict:
    cover_letter = state.get("cover_letter")
    user_name = state.get("resume_info", {}).get("name", "Candidate")
    job_title = state.get("job_info", {}).get("title", "the position")

    # Write to a file (optional)
    filename = f"cover_letter_{user_name.replace(' ', '_')}_{job_title.replace(' ', '_')}.txt"
    with open(filename, "w") as f:
        f.write(cover_letter)

    # Optionally log or print
    print("\n✅ Final cover letter saved as:", filename)

    # Store in state
    state["export_path"] = filename
    return state



# Add nodes
graph.add_node("parse_job", job_parser_node)
graph.add_node("parse_resume", resume_parser_node)
graph.add_node("match", relevance_matcher_node)
graph.add_node("generate", cover_letter_generator_node)
graph.add_node("validate", cover_letter_validator_node)
graph.add_node("export", exporter_node)

# Add edges
graph.set_entry_point("parse_job")
graph.add_edge("parse_job", "parse_resume")
graph.add_edge("parse_resume", "match")
graph.add_edge("match", "generate")
graph.add_edge("generate", "validate")

# Conditional edge: validator controls flow
def validate_branch(state):
    if state["validation_result"]["valid"]:
        return "export"
    else:
        return "generate"

graph.add_conditional_edges("validate", validate_branch)

graph.set_finish_point("export")

app = graph.compile()
final_state = app.invoke(initial_state)
