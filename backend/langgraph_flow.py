import os
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph
import json
from typing import TypedDict, List, Optional
import re
from dotenv import load_dotenv
import time
import random
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
    input_validation: dict
    validation_failed: bool
    validation_error: dict

def create_claude_with_retry(model, **kwargs):
    """Create a Claude model with retry logic"""
    return ChatAnthropic(
        model=model,
        anthropic_api_key=api_key,
        **kwargs
    )

def invoke_with_retry(model, prompt, max_retries=3, base_delay=1):
    """Invoke Claude with exponential backoff retry logic"""
    for attempt in range(max_retries):
        try:
            return model.invoke(prompt)
        except Exception as e:
            # Check if it's an overload or rate limit error
            if "529" in str(e) or "overloaded" in str(e).lower():
                if attempt == max_retries - 1:
                    raise e
                
                # Exponential backoff with jitter
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"API overloaded, retrying in {delay:.2f} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
            elif "rate limit" in str(e).lower():
                if attempt == max_retries - 1:
                    raise e
                
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limit hit, retrying in {delay:.2f} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
            else:
                # For other errors, don't retry
                raise e
    
    raise Exception("Max retries exceeded")

#setting up claude client
claude = create_claude_with_retry(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024
)

claude_parser_job = create_claude_with_retry(
    model="claude-3-7-sonnet-20250219",
    temperature=0.2,
    max_tokens=512
)

claude_parser_resume = create_claude_with_retry(
    model="claude-3-7-sonnet-20250219",
    temperature=0.2,
    max_tokens=1024
)

claude_matcher = create_claude_with_retry(
    model="claude-3-7-sonnet-20250219",
    temperature=0.3,
    max_tokens=512
)

generator_system_prompt = (
    "You are a professional writing agent specialized in generating high-quality, concise, and direct cover letters.\n"
    "Your goal is to transform structured input (job info, resume details, tone, matched experiences) into a well-formed, professional letter.\n"
    "You always write in a way that is clear, specific, and impactful — never verbose, flowery, or overly warm.\n"
    "You do not hallucinate facts. You only use information given to you.\n"
    "Prioritize clarity, professionalism, and brevity over emotional tone.\n"
    "Assume this draft will be reviewed and improved by the user. Focus on clarity and professional insight."
)

claude_generator = create_claude_with_retry(
    model="claude-opus-4-20250514",
    temperature=0.6,
    max_tokens=1024,
    system=generator_system_prompt
)

validator_system_prompt = (
    "You are a strict and intelligent QA assistant for AI-generated cover letters.\n"
    "Your job is to evaluate whether a cover letter meets specific content, tone, and formatting requirements.\n"
    "You never rewrite the letter. You only return a judgment (valid or not) and a list of clear, actionable issues.\n"
    "You do not ignore minor problems if they affect clarity, tone, or human authenticity.\n"
    "You aim to ensure that every letter sounds human, specific, and emotionally aware — never generic or robotic.\n"
    "You only use the evaluation criteria provided to you, and never make up new ones."
)

claude_validator = create_claude_with_retry(
    model="claude-3-7-sonnet-20250219",
    temperature=0.0,
    max_tokens=512,
    system=validator_system_prompt
)

claude_input_validation = create_claude_with_retry(
    model="claude-3-5-haiku-20241022",
    temperature=0.0,
    max_tokens=256
)

graph = StateGraph(CoverLetterState)

def extract_json_from_markdown(text):
    # Try to extract JSON from triple backticks
    match = re.search(r"```(?:json)?\\n?(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Try to find the first { ... } block
    match = re.search(r"({.*})", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: return the text as is
    return text.strip()

def safe_filename(s):
    return re.sub(r'[^\w\-]', '_', s)

def clean_json_string(s):
    import re
    # Remove trailing commas before } or ]
    s = re.sub(r',([ \t\r\n]*[}\]])', r'\1', s)
    # Remove any non-JSON text before/after the first/last curly brace
    match = re.search(r'({.*})', s, re.DOTALL)
    if match:
        s = match.group(1)
    return s

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
    
    print("Trying to parse:", repr(content))
    
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
            
    except json.JSONDecodeError as e:
        print("Invalid JSON from Claude in input_validation_node:", content)
        print("Exception:", e)
        state["input_validation"] = {"resume_valid": False, "job_valid": False}
        state["validation_failed"] = True
        state["validation_error"] = {
            "resume_issues": ["Failed to validate input"],
            "job_issues": ["Failed to validate input"]
        }
    
    return state


def job_parser_node(state: dict) -> dict:
    if "job_info" in state and state["job_info"]:
        return state
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
    try:
        response = invoke_with_retry(claude_parser_job, prompt)
        content = extract_json_from_markdown(response.content)
        if not content:
            print("Claude returned empty response in job_parser_node.")
            state["job_info"] = {}
            return state
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            print("Claude returned invalid JSON in job_parser_node")
            state["job_info"] = {}
            return state
        
        state["job_info"] = parsed
        return state
    except Exception as e:
        print(f"Error in job_parser_node: {e}")
        state["job_info"] = {
            "title": "Position",
            "company": "Company",
            "required_skills": [],
            "values": [],
            "summary": "Job description"
        }
        return state


def resume_parser_node(state: dict) -> dict:
    if "resume_info" in state and state["resume_info"]:
        # Also set user_name if it's not already set
        if "user_name" not in state and state["resume_info"].get("name"):
            state["user_name"] = state["resume_info"]["name"]
        return state 
    resume_text = state["resume_posting"]
    prompt = f"""
You are an intelligent assistant that extracts structured information from resumes to help generate personalized cover letters.

Please read the resume below and return a JSON object with the following fields:

- "name": The person's full name
- "experiences": A list of work experiences, each containing:
    - "title": Job title
    - "organization": Company/organization name
    - "duration": Time period (if available)
    - "description": Brief description of role and achievements
    - "skills_used": List of technical or domain-specific skills used in that experience
- "skills": A deduplicated list of skills explicitly or implicitly mentioned (e.g., Python, SQL, tutoring, machine learning, communication).
- "education": A list of schools or degrees, including:
    - "institution"
    - "degree"
    - "field"
    - "graduation_year" (if available)

Only extract what's present in the text - do not guess or hallucinate. Return ONLY the JSON object. Do not include triple backticks or any text before or after the JSON. Double-check that your output is valid JSON. Do not omit any commas or brackets.

### Resume:
{resume_text}
"""

    try:
        response = invoke_with_retry(claude_parser_resume, prompt)
        content = extract_json_from_markdown(response.content)
        cleaned = clean_json_string(content)
        try:
            parsed = json.loads(cleaned)
            state["resume_info"] = parsed
            state["user_name"] = parsed.get("name", "Candidate")
            print("Resume parsed successfully")
        except json.JSONDecodeError as e:
            print("Claude returned invalid JSON for resume")
            print("Exception:", e)
            # Fallback: re-prompt Claude to fix the JSON
            fix_prompt = f"""
Your previous response was not valid JSON. Please return the same data as valid JSON only. Do not include any explanations, comments, or extra text. Only output a valid JSON object.\n\nHere is your previous response:\n\n{cleaned}
"""
            try:
                fix_response = invoke_with_retry(claude_parser_resume, fix_prompt)
                fix_content = extract_json_from_markdown(fix_response.content)
                fix_cleaned = clean_json_string(fix_content)
                parsed = json.loads(fix_cleaned)
                state["resume_info"] = parsed
                state["user_name"] = parsed.get("name", "Candidate")
                print("Resume parsed successfully (fallback)")
            except Exception as e2:
                print("Fallback also failed")
                print("Exception:", e2)
                state["resume_info"] = {}
                state["user_name"] = "Candidate"
    except Exception as e:
        print(f"Error in resume_parser_node: {e}")
        # Provide fallback behavior
        state["resume_info"] = {
            "name": "Candidate",
            "experiences": [],
            "skills": [],
            "education": []
        }
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
        print("Relevance matching completed successfully")
        parsed = json.loads(content)
        state["matched_experiences"] = parsed.get("matched_experiences", [])
    except json.JSONDecodeError:
        print("Invalid JSON from Claude in relevance_matcher_node")
        state["matched_experiences"] = []
    return state


def cover_letter_generator_node(state: dict) -> dict:
    job = state["job_info"]
    experiences = state["matched_experiences"]
    user_name = state.get("user_name", "Candidate")
    prior_issues = state.get("prior_issues", [])
    tone = job.get("tone", "Professional, concise, and clearly tailored to the role. Direct, specific, and achievement-focused. Avoids filler, excessive warmth, or verbosity.")

    prompt = f"""
Write a 250–350 word cover letter using the information below.

Requirements:
1. Begin with a formal greeting: e.g., "Dear [Team/Manager] at {job.get('company', 'the company')}".
2. Intro paragraph: state the job title, company name, and express clear enthusiasm.
3. Body: highlight 1–2 key experiences that demonstrate **transferable skills** applicable to this role. Focus on:
   - How their existing experience translates to the job requirements
   - Specific skills that transfer well (e.g., problem-solving, teamwork, analysis, communication, programming, research)
   - Quantifiable achievements or outcomes from their experience
   - Learning ability and adaptability
   - If no exact matches exist, emphasize transferable skills from their background
4. Closing: reinforce interest, connect to the company's mission, and invite further discussion.
5. End with: "Sincerely, {user_name}"

**CRITICAL HONESTY GUIDELINES:**
- **NEVER fabricate, invent, or stretch experience** - only use information that is explicitly provided
- **Be completely truthful** about the candidate's actual experience and skills
- **Focus on transferable skills** - Show how existing experience applies to the new role
- **Be specific about skills** - Programming, analysis, teamwork, communication, etc.
- **Highlight learning ability** - Demonstrate adaptability and growth mindset
- **Use concrete examples** - Reference specific projects, courses, or experiences from the resume
- **Maintain a {tone} tone throughout**
- **Be concise and direct, avoiding flowery language**
- **Emphasize potential and transferability** rather than direct experience matches
- **If no exact matches, focus on transferable skills** from their existing background
- **PRIORITIZE HONESTY OVER PERFECTION** - It's better to be honest about limitations than to fabricate experience
- **KEEP IT CONCISE** - Aim for 250-350 words, be direct and to-the-point
- **BE CONFIDENT** - Focus on strengths and transferable skills, don't apologize for gaps
- **EMPHASIZE POTENTIAL** - Show enthusiasm for learning and growth opportunities

### Job Description:
{job}

### Matched Experiences:
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

    validator_prompt = f"""
You are a quality assurance assistant for AI-generated cover letters. Your PRIMARY goal is to ensure letters are HONEST and truthful.

Evaluate the letter below using these criteria:

1. **HONESTY AND TRUTHFULNESS** — Does the letter honestly represent the candidate's experience without ANY fabrication? This is the MOST IMPORTANT criterion.
2. **Company and Job Mention** — Does it clearly mention the company name and job title?
3. **Transferable Skills Focus** — Does it effectively connect the candidate's background to the job through transferable skills? For example:
   - Programming experience → web development skills
   - Git experience → version control and collaboration
   - Research/analysis skills → problem-solving and attention to detail
   - Teamwork experience → collaboration and communication
   - Coursework/projects → relevant technical skills
4. **Tone and Professionalism** — Is the tone appropriate, professional, and confident?
5. **Length and Structure** — Is it well-structured and appropriately sized (250-350 words)?

**CRITICAL HONESTY RULES**: 
- **REJECT letters** that make ANY false claims about experience, skills, or qualifications
- **REJECT letters** that fabricate or invent experience not present in the resume
- **REJECT letters** that claim expertise in technologies not mentioned
- **ACCEPT letters** that are honest about limitations and focus on transferable skills
- **PRIORITIZE HONESTY OVER PERFECTION** - A truthful letter with gaps is better than a fabricated perfect letter
- **Be flexible** about direct experience requirements if the candidate shows relevant transferable skills
- **ENCOURAGE CONFIDENCE** - Letters should focus on strengths and potential, not apologize for gaps

Return a JSON object with:
- "valid": true or false
- "issues": list of concrete problems if found. Be constructive and specific.

DO NOT return anything except the JSON object. No commentary. No markdown. No extra text.

### Cover Letter:
{letter}

### Job Info:
{job}
"""

    response = claude_validator.invoke(validator_prompt)
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

    # Sanitize filename to avoid slashes and problematic characters
    filename = f"cover_letter_{safe_filename(user_name)}_{safe_filename(job_title)}.txt"
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

