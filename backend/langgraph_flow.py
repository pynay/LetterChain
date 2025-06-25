import os
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph
import json
from typing import TypedDict, List, Optional
import re
from dotenv import load_dotenv
load_dotenv()
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

claude_parser_job = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",
    temperature=0.2,
    max_tokens=512,
    anthropic_api_key=api_key
)

claude_parser_resume = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",
    temperature=0.2,
    max_tokens=1024,
    anthropic_api_key=api_key
)


claude_matcher = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",
    temperature=0.3,
    max_tokens=512,
    anthropic_api_key=api_key
)


claude_generator = ChatAnthropic(
    model="claude-opus-4-20250514",
    temperature=0.6,
    max_tokens=1024,
    anthropic_api_key=api_key
)


claude_validator = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",
    temperature=0.0,
    max_tokens=512,
    anthropic_api_key=api_key
)

claude_input_validation = ChatAnthropic(
    model="claude-3-5-haiku-20241022",
    temperature=0.0,
    max_tokens=256,
    anthropic_api_key=api_key
)



graph = StateGraph(CoverLetterState)

def extract_json_from_markdown(text):
    match = re.search(r"```(?:json)?\\n?(.*)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

#DEFINING ALL THE NODES FOR LANGGRAPH

def input_validation_node(state: dict) -> dict:
    resume_text = state["resume_posting"]
    job_posting = state["job_posting"]

    prompt = f"""
You are a quality control assistant that validates whether uploaded documents are legitimate resumes and job descriptions.

Analyze the two provided texts and determine if they are valid inputs for a cover letter generator.

Return ONLY a JSON object with this structure:
{{
  "resume_valid": true/false,
  "job_valid": true/false,
  "resume_issues": ["list of specific problems with resume, if any"],
  "job_issues": ["list of specific problems with job description, if any"]
}}

**Resume Validation Criteria:**
- Contains personal information (name, contact details)
- Lists work experience, education, or skills
- Is not random text, code, or unrelated content
- Has reasonable length (at least 100 characters)

**Job Description Validation Criteria:**
- Contains job title and company information
- Lists responsibilities, requirements, or qualifications
- Is not random text, code, or unrelated content
- Has reasonable length (at least 100 characters)

Be strict but fair. If either input is clearly not a resume or job description, mark it as invalid.

### Resume Text:
{resume_text[:2000]}...

### Job Description Text:
{job_posting[:2000]}...


"""
    response = claude_input_validation.invoke(prompt)
    content = extract_json_from_markdown(response.content)
    
    try:
        validation_result = json.loads(content)
        state["input_validation"] = validation_result
        
        # Check if either input is invalid
        if not validation_result.get("resume_valid", True) or not validation_result.get("job_valid", True):
            state["validation_failed"] = True
            state["validation_error"] = {
                "resume_issues": validation_result.get("resume_issues", []),
                "job_issues": validation_result.get("job_issues", [])
            }
        else:
            state["validation_failed"] = False
            
    except json.JSONDecodeError:
        print("Invalid JSON from Claude in input_validation_node:", content)
        state["input_validation"] = {"resume_valid": False, "job_valid": False}
        state["validation_failed"] = True
        state["validation_error"] = {
            "resume_issues": ["Failed to validate input"],
            "job_issues": ["Failed to validate input"]
        }
    
    return state


def job_parser_node(state: dict) -> dict:
    job_posting = state["job_posting"]
    prompt = f"""
You are an intelligent assistant helping generate personalized cover letters by extracting structured information from job postings.

Please read the job description below and return a JSON object with the following fields:

- "title"
- "company"
- "required_skills" (list)
- "values" (list)
- "summary" (2–3 sentences)

Return ONLY the JSON object. Do not include triple backticks or any text before or after the JSON.

### Job Description:
{job_posting}
"""
    response = claude_parser_job.invoke(prompt)
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

    response = claude_parser_resume.invoke(prompt)
    content = extract_json_from_markdown(response.content)
    try:
        parsed = json.loads(content)
        state["resume_info"] = parsed
        state["user_name"] = parsed.get("name", "Candidate")
        print("Resume Testing: ", content)
    except json.JSONDecodeError:
        print("Claude returned invalid JSON for resume. Response:", content)
        state["resume_info"] = {}  # Or handle as appropriate
        state["user_name"] = "Candidate"
    return state


def relevance_matcher_node(state: dict) -> dict:
    resume_info = state.get("resume_info")
    job_info = state.get("job_info")
    if not resume_info or not job_info:
        print("Missing resume_info or job_info, skipping relevance matching.")
        state["matched_experiences"] = []
        return state

    prompt = f"""
You are an assistant that compares a candidate's structured resume data with a job description to identify the most relevant content to highlight in a personalized cover letter.

Your task is to select 2–3 **highly relevant experiences** that align well with the job's requirements. In addition to work experience, you may also consider:

- Technical coursework
- Projects
- Research
- Teaching or instructional roles
- Strong skill matches (if clearly demonstrated)

Each selected item must:
- Be directly present in the resume data (DO NOT invent or hallucinate)
- Map clearly to some aspect of the job description

Return ONLY a JSON object in the following format:
{{
  "matched_experiences": [
    {{
      "type": "experience" | "project" | "coursework" | "instruction" | "skill",
      "title": "...",
      "organization": "...",  // For coursework use school, for projects use project name
      "reason": "Why this is a strong match for the job, based on the job description"
    }}
  ]
}}

Do not include any explanations, markdown, or extra text — only return the raw JSON object.

### Resume Data:
{resume_info}

### Job Description:
{job_info}
"""

    
    response = claude_matcher.invoke(prompt)
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
    user_name = state.get("user_name", "Candidate")
    prior_issues = state.get("prior_issues", [])
    tone = job.get("tone", "Emotionally intelligent, detailed, and clearly tailored to the role and mission. Shows initiative, reflection, and care - top tier cover letter.")

    
    prompt = f"""
You are a helpful assistant that writes tailored, one-page cover letters using structured data from a candidate's resume and a job description.

Your task is to generate a professional, specific, and concise cover letter that includes the following:

1. A formal greeting addressed directly to the company and job title (e.g., "Dear [Team/Manager] at {job.get('company', 'the company')}").
2. An introductory paragraph that clearly states the position being applied for and expresses enthusiasm.
3. Two to three **distinct and relevant experiences** from the candidate that directly match the job's responsibilities or values.
4. A closing paragraph that reinforces interest, aligns with the company's mission/values, and invites further discussion.
5. A sign-off that ends with "Sincerely," followed by the candidate's full name: **{user_name}**

🛑 **Constraints**:
- You may only use the information provided. Do NOT invent experiences, skills, or facts that are not explicitly included in the structured input.
- Maintain a {tone} tone throughout.
- Do not include headers, placeholders, or markdown formatting, do not use ANY em dashes.
- Keep the letter within 400–500 words.

### Job Description Summary:
{job}

### Candidate's Matched Experiences:
{experiences}
"""


    if prior_issues:
        issue_str = "\n".join(f"- {issue}" for issue in prior_issues)
        prompt += f"""

The previous draft of this letter was rejected for the following reasons. Please address them:
{issue_str}
"""

    response = claude_generator.invoke(prompt)
    state["cover_letter"] = response.content
    return state


def cover_letter_validator_node(state: dict) -> dict:
    letter = state["cover_letter"]
    job = state["job_info"]
    tone = job.get("tone", "formal")

    prompt = f"""
You are a meticulous quality assurance assistant for AI-generated cover letters. Your standards are high.

Evaluate the following cover letter according to these strict criteria:

1. **Company and Job Mention**: Does it clearly and correctly mention the exact company name and job title as stated in the job description?
2. **Experience Relevance**: Does it highlight at least two distinct, concrete experiences that clearly align with the specific responsibilities or qualifications listed in the job?
3. **Tone Accuracy**: Does it maintain the required tone ("{tone}") consistently, avoiding mechanical, stiff, or overly formal phrasing?
4. **Specificity and Depth**: Is the letter tailored and thoughtful — does it avoid vague language, clichés, and filler? Does it demonstrate actual familiarity with the company, mission, or product?
5. **Human and Personal Voice**: Does it sound like a real person wrote it? Is there genuine personality, motivation, or reflection conveyed, rather than formulaic or AI-sounding language?
6. **Length Constraint**: Is the letter under one page (max ~500 words)?

Return a JSON object with:
- "valid": true or false
- "issues": a list of strings describing problems found, if any. Be blunt, specific, and critical.

Only return the JSON object. No commentary. No triple backticks.

### Cover Letter:
{letter}

### Job Info:
{job}
"""


    response = claude_validator.invoke(prompt)
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
    user_name = state.get("user_name", "Candidate")
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
graph.add_node("validate_input", input_validation_node)
graph.add_node("parse_job", job_parser_node)
graph.add_node("parse_resume", resume_parser_node)
graph.add_node("match", relevance_matcher_node)
graph.add_node("generate", cover_letter_generator_node)
graph.add_node("validate", cover_letter_validator_node)
graph.add_node("export", exporter_node)
# Add error node for validation failures

def error_node(state: dict) -> dict:
    # This node is reached if input validation fails
    return state

graph.add_node("error", error_node)

# Add edges
graph.set_entry_point("validate_input")
graph.add_edge("parse_job", "parse_resume")
graph.add_edge("parse_resume", "match")
graph.add_edge("match", "generate")
graph.add_edge("generate", "validate")

def input_validation_branch(state): 
    if state.get("validation_failed", False):
        return "error"
    else:
        return "parse_job"
# Conditional edge: validator controls flow
def validate_branch(state):
    result = state.get("validation_result", {})
    if result.get("valid", False):
        return "export"
    else:
        return "generate"


graph.add_conditional_edges(
    "validate_input", input_validation_branch,
    {
        "error": "error",
        "parse_job": "parse_job"
    }
)

graph.add_conditional_edges(
    "validate",
    validate_branch,
    {
      "export": "export",
           "generate": "generate"
    }
)
graph.set_finish_point("export")
graph.set_finish_point("error")

app_graph = graph.compile()

