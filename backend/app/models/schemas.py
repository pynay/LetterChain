import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum

class ToneEnum(str, Enum):
    PROFESSIONAL = "Professional, concise, and clearly tailored to the role. Direct, specific, and achievement-focused. Avoids filler, excessive warmth, or verbosity."
    EMOTIONAL = "Emotionally intelligent, detailed, and clearly tailored to the role and mission. Shows initiative, reflection, and care — top-tier cover letter."
    CONFIDENT = "Confident, enthusiastic, and results-oriented. Emphasizes achievements and impact."
    CREATIVE = "Creative, innovative, and forward-thinking. Shows unique perspective and problem-solving approach."


class FileUploadResponse(BaseModel):
    """Response model for file upload validation"""
    filename: str
    size: int
    content_type: str
    is_valid: bool
    error_message: Optional[str] = None

class ResumeInfo(BaseModel):
    """Structured resume information"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    summary: Optional[str] = None

class JobInfo(BaseModel):
    """Structured job information"""
    title: str
    company: str
    location: Optional[str] = None
    requirements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    tone: str = ToneEnum.PROFESSIONAL

class MatchedExperience(BaseModel):
    """Experience matched to job requirements"""
    experience_type: str  # "work", "education", "project"
    title: str
    description: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    transferable_skills: List[str] = Field(default_factory=list)

class CoverLetterRequest(BaseModel):
    """Request model for cover letter generation"""
    resume_text: str = Field(..., min_length=100, description="Resume content")
    job_text: str = Field(..., min_length=100, description="Job description")
    tone: ToneEnum = ToneEnum.PROFESSIONAL
    user_name: Optional[str] = None
    
    @field_validator('resume_text', 'job_text')
    @classmethod
    def validate_text_length(cls, v):
        if len(v.strip()) < 100:
            raise ValueError('Text must be at least 100 characters long')
        return v.strip()

class CoverLetterResponse(BaseModel):
    """Response model for generated cover letter"""
    cover_letter: str
    job_info: JobInfo
    resume_info: ResumeInfo
    matched_experiences: List[MatchedExperience]
    generation_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "cover_letter": "Dear Hiring Manager at TechCorp...",
                "job_info": {
                    "title": "Software Engineer",
                    "company": "TechCorp",
                    "requirements": ["Python", "FastAPI"]
                },
                "resume_info": {
                    "name": "John Doe",
                    "experience": [{"title": "Developer", "company": "Startup"}]
                },
                "matched_experiences": [
                    {
                        "experience_type": "work",
                        "title": "Software Developer",
                        "relevance_score": 0.85,
                        "transferable_skills": ["Python", "Problem Solving"]
                    }
                ],
                "generation_metadata": {
                    "iterations": 1,
                    "validation_passed": True,
                    "generation_time_ms": 2500
                }
            }
        }

class FeedbackRequest(BaseModel):
    """Request model for cover letter feedback"""
    cover_letter: str = Field(..., min_length=50)
    user_feedback: str = Field(..., min_length=10)
    resume_text: str
    job_text: str
    tone: ToneEnum = ToneEnum.PROFESSIONAL

class ValidationResult(BaseModel):
    """Result of cover letter validation"""
    valid: bool
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    score: float = Field(ge=0.0, le=1.0, description="Quality score from 0-1")

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: str(datetime.utcnow()))