from typing import Dict, Any
import json
import logging
from app.core.tracing import tracing_service
from app.services.ai_service import ai_service
from app.models.schemas import ValidationResult

logger = logging.getLogger(__name__)

@tracing_service.trace_node("input_validation")
def input_validation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Validate input documents are legitimate resumes and job descriptions"""
    
    resume_text = state["resume_posting"]
    job_posting = state["job_posting"]
    
    system_prompt = """You are a quality control assistant that validates whether uploaded documents are legitimate resumes and job descriptions.

Return ONLY a JSON object with this structure:
{
  "resume_valid": true/false,
  "job_valid": true/false,
  "resume_issues": ["list of specific problems with resume, if any"],
  "job_issues": ["list of specific problems with job description, if any"]
}

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

Be strict but fair. If either input is clearly not a resume or job description, mark it as invalid."""
    
    prompt = f"{system_prompt}\n\n### Resume Text:\n{resume_text[:2000]}...\n\n### Job Description Text:\n{job_posting[:2000]}..."
    
    try:
        response = ai_service.invoke_with_retry(
            model_name="claude-3-5-haiku",
            prompt=prompt,
            metadata={"operation": "input_validation"}
        )
        
        validation_data = ai_service._parse_json_response(response)
        
        state["input_validation"] = validation_data
        
        # Check if validation failed
        if not validation_data.get("resume_valid", False) or not validation_data.get("job_valid", False):
            state["validation_failed"] = True
            state["validation_error"] = {
                "resume_issues": validation_data.get("resume_issues", []),
                "job_issues": validation_data.get("job_issues", [])
            }
        
        return state
        
    except Exception as e:
        logger.error(f"Input validation failed: {str(e)}")
        state["validation_failed"] = True
        state["validation_error"] = {"error": str(e)}
        return state

@tracing_service.trace_node("resume_parser")
def resume_parser_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Parse resume text into structured data"""
    
    resume_text = state["resume_posting"]
    
    try:
        parsed_resume = ai_service.parse_resume(resume_text)
        state["resume_info"] = parsed_resume
        
        # Extract user name for personalization
        if "name" in parsed_resume:
            state["user_name"] = parsed_resume["name"]
        
        return state
        
    except Exception as e:
        logger.error(f"Resume parsing failed: {str(e)}")
        # Provide fallback data
        state["resume_info"] = {
            "name": "Candidate",
            "experience": [],
            "education": [],
            "skills": []
        }
        state["user_name"] = "Candidate"
        return state

@tracing_service.trace_node("job_parser")
def job_parser_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Parse job description into structured data"""
    job_text = state["job_posting"]
    try:
        parsed_job = ai_service.parse_job(job_text)
        logger.info(f"job_parser_node: parsed_job = {parsed_job}")
        if not parsed_job or not isinstance(parsed_job, dict):
            logger.error("job_parser_node: parse_job returned None or invalid data")
            # Provide fallback data
            state["job_info"] = {
                "title": "Position",
                "company": "Company",
                "requirements": [],
                "responsibilities": []
            }
        else:
            state["job_info"] = parsed_job
        return state
    except Exception as e:
        logger.error(f"Job parsing failed: {str(e)}")
        # Provide fallback data
        state["job_info"] = {
            "title": "Position",
            "company": "Company",
            "requirements": [],
            "responsibilities": []
        }
        return state

@tracing_service.trace_node("relevance_matcher")
def relevance_matcher_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Match resume experiences to job requirements"""
    
    resume_info = state["resume_info"]
    job_info = state["job_info"]
    
    system_prompt = """You are an expert at matching candidate experiences to job requirements.

Analyze the resume experiences and job requirements to find the best matches. Focus on transferable skills and relevant experience.

Return ONLY a JSON object with this structure:
{
  "matched_experiences": [
    {
      "experience_type": "work|education|project",
      "title": "string",
      "description": "string", 
      "relevance_score": 0.0-1.0,
      "transferable_skills": ["skill1", "skill2"]
    }
  ]
}

Prioritize experiences that demonstrate transferable skills relevant to the job requirements."""
    
    prompt = f"{system_prompt}\n\n### Resume Info:\n{json.dumps(resume_info, indent=2)}\n\n### Job Info:\n{json.dumps(job_info, indent=2)}"
    
    try:
        response = ai_service.invoke_with_retry(
            model_name="claude-3-7-sonnet",
            prompt=prompt,
            metadata={"operation": "relevance_matching"}
        )
        
        matching_data = ai_service._parse_json_response(response)
        state["matched_experiences"] = matching_data.get("matched_experiences", [])
        
        return state
        
    except Exception as e:
        logger.error(f"Relevance matching failed: {str(e)}")
        state["matched_experiences"] = []
        return state

@tracing_service.trace_node("cover_letter_generator")
def cover_letter_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate cover letter from matched experiences"""
    
    job_info = state["job_info"]
    experiences = state["matched_experiences"]
    user_name = state.get("user_name", "Candidate")
    prior_issues = state.get("prior_issues", [])
    tone = state.get("tone", "Professional, concise, and clearly tailored to the role.")
    
    system_prompt = f"""You are a professional writing agent specialized in generating high-quality, concise, and direct cover letters.

Write a 250–350 word cover letter using the information provided.

Requirements:
1. Begin with a formal greeting: e.g., "Dear [Team/Manager] at {{company}}".
2. Intro paragraph: state the job title, company name, and express clear enthusiasm.
3. Body: highlight 1–2 key experiences that demonstrate **transferable skills** applicable to this role.
4. Closing: reinforce interest, connect to the company's mission, and invite further discussion.
5. End with: "Sincerely, {user_name}"

**STRICT GUIDELINES:**
- **NEVER fabricate, invent, or stretch experience** — only use information that is explicitly provided. Do not hallucinate or make up any experience, skills, or qualifications.
- **If there are no direct experience matches, write an honest cover letter that highlights any transferable skills, strengths, or relevant qualities from the resume that could apply to the job. Do your best to connect the candidate's real background to the job requirements.**
- **Do NOT include language that highlights flaws, gaps, or self-doubt** (e.g., "While I am still developing...", "Although I lack...", "I am early in my career", "I have limited experience in...").
- **Do NOT include self-disqualifying or underconfident language**. Focus on strengths, achievements, and readiness.
- **Be completely truthful and specific** about the candidate's actual experience and skills.
- **Focus on transferable skills** — Show how existing experience applies to the new role.
- **Be specific about skills** — Programming, analysis, teamwork, communication, etc.
- **Highlight learning ability** — Demonstrate adaptability and growth mindset, but only if supported by the resume.
- **Use concrete examples** — Reference specific projects, courses, or experiences from the resume.
- **Maintain a {tone} tone throughout**
- **Be concise and direct, avoiding flowery language**
- **Emphasize potential and transferability** rather than direct experience matches
- **PRIORITIZE HONESTY OVER PERFECTION** — It's better to be honest about limitations than to fabricate experience

**CONFIDENCE AND TONE GUIDELINES:**
- **Always present the candidate in a confident, positive light**
- **Do not include language that downplays abilities or suggests unqualification**
- **Avoid phrases like "While I am still developing..." or "Although I lack..."**
- **If mentioning skills that are being developed, frame them as strengths or evidence of adaptability**
- **Focus on what the candidate CAN do and WILL contribute, not what they cannot do**
- **Use language that shows eagerness to learn and grow, not inadequacy**
- **Maintain enthusiasm and conviction throughout the letter**"""
    
    prompt = f"{system_prompt}\n\n### Job Description:\n{json.dumps(job_info, indent=2)}\n\n### Matched Experiences:\n{json.dumps(experiences, indent=2)}"
    
    if prior_issues:
        issue_str = "\n".join(f"- {issue}" for issue in prior_issues)
        prompt += f"\n\nThe previous draft was rejected for the following reasons. Please address them:\n{issue_str}"
    
    try:
        response = ai_service.invoke_with_retry(
            model_name="claude-opus-4",
            prompt=prompt,
            metadata={
                "operation": "cover_letter_generation",
                "prior_issues_count": len(prior_issues),
                "matched_experiences_count": len(experiences)
            }
        )
        
        state["cover_letter"] = response
        return state
        
    except Exception as e:
        logger.error(f"Cover letter generation failed: {str(e)}")
        state["cover_letter"] = "Error generating cover letter. Please try again."
        return state

@tracing_service.trace_node("cover_letter_validator")
def cover_letter_validator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Validate generated cover letter quality"""
    
    letter = state["cover_letter"]
    job_info = state["job_info"]
    
    system_prompt = """You are a very strict and intelligent QA assistant for AI-generated cover letters.

Evaluate the letter using these criteria:

1. **HONESTY AND TRUTHFULNESS** — Does the letter honestly represent the candidate's experience without ANY fabrication, exaggeration, or hallucination? Even minor exaggerations, vague claims, or made-up details should be flagged.
2. **Company and Job Mention** — Does it clearly mention the company name and job title?
3. **Transferable Skills Focus** — Does it effectively connect the candidate's background to the job through specific, concrete transferable skills? Generic or overly flattering language should be flagged.
4. **Tone and Professionalism** — Is the tone appropriate, professional, and confident? Letters that are too generic, overly flattering, or lack specific, relevant details should be rejected.
5. **Length and Structure** — Is it well-structured and appropriately sized (250-350 words)? Letters that are too short, too long, or poorly structured should be rejected.
6. **NO SELF-DISQUALIFYING OR FLAW-HIGHLIGHTING LANGUAGE** — REJECT any letter that includes language about flaws, gaps, self-doubt, or underconfidence (e.g., "While I am still developing...", "Although I lack...", "I am early in my career", "I have limited experience in..."). The letter should focus on strengths and achievements.
7. **TRANSFERABLE SKILLS ARE ACCEPTABLE** — If there are no direct experience matches, it is acceptable for the letter to focus on transferable skills or general strengths from the resume, as long as it does not fabricate or exaggerate. Only reject if the letter fabricates, exaggerates, or is completely irrelevant.

Return a JSON object with:
- "valid": true or false
- "issues": list of concrete problems if found
- "score": quality score from 0.0 to 1.0

**STRICT HONESTY RULES**:
- **REJECT letters** that make ANY false, exaggerated, or hallucinated claims about experience, skills, or qualifications
- **REJECT letters** that are generic, vague, or lack specific, relevant details
- **REJECT letters** that use overly flattering or flowery language without evidence
- **REJECT letters** that include self-disqualifying, flaw-highlighting, or underconfident language
- **ACCEPT letters** that are honest, specific, and focused on transferable skills and strengths, even if there are no direct experience matches
- **PRIORITIZE HONESTY AND SPECIFICITY OVER PERFECTION** — A truthful, specific letter with gaps is better than a generic or fabricated perfect letter"""
    
    prompt = f"{system_prompt}\n\n### Cover Letter:\n{letter}\n\n### Job Info:\n{json.dumps(job_info, indent=2)}"
    
    try:
        response = ai_service.invoke_with_retry(
            model_name="claude-3-7-sonnet",
            prompt=prompt,
            metadata={"operation": "cover_letter_validation"}
        )
        
        validation_data = ai_service._parse_json_response(response)
        state["validation_result"] = validation_data
        
        if not validation_data.get("valid", False):
            state["prior_issues"] = validation_data.get("issues", [])
        
        return state
        
    except Exception as e:
        logger.error(f"Cover letter validation failed: {str(e)}")
        state["validation_result"] = {
            "valid": False,
            "issues": ["Validation failed due to technical error"],
            "score": 0.0
        }
        return state