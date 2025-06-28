from typing import TypedDict, List, Optional, Dict, Any
from pydantic import BaseModel

class CoverLetterState(TypedDict, total=False):
    """Type-safe state definition for LangGraph workflow"""
    resume_posting: str
    job_posting: str
    tone: str
    user_name: Optional[str]
    
    # Parsed data
    resume_info: Dict[str, Any]
    job_info: Dict[str, Any]
    
    # Processing data
    matched_experiences: List[Dict[str, Any]]
    cover_letter: str
    
    # Validation data
    validation_result: Dict[str, Any]
    prior_issues: Optional[List[str]]
    input_validation: Dict[str, Any]
    validation_failed: bool
    validation_error: Dict[str, Any]
    
    # Output data
    export_path: Optional[str]
    generation_metadata: Dict[str, Any]


class StateValidator(BaseModel):
    """Validator for LangGraph state transitions"""
    
    @staticmethod
    def validate_initial_state(state: CoverLetterState) -> bool:
        """Validate that initial state has required fields"""
        required_fields = ["resume_posting", "job_posting"]
        return all(field in state for field in required_fields)
    
    @staticmethod
    def validate_parsed_state(state: CoverLetterState) -> bool:
        """Validate that parsing is complete"""
        required_fields = ["resume_info", "job_info"]
        return all(field in state for field in required_fields)
    
    @staticmethod
    def validate_generation_state(state: CoverLetterState) -> bool:
        """Validate that generation is complete"""
        return "cover_letter" in state and state["cover_letter"]
    
    @staticmethod
    def get_state_summary(state: CoverLetterState) -> Dict[str, Any]:
        """Get a summary of current state for logging"""
        return {
            "has_resume": "resume_posting" in state,
            "has_job": "job_posting" in state,
            "resume_parsed": "resume_info" in state,
            "job_parsed": "job_info" in state,
            "experiences_matched": "matched_experiences" in state,
            "letter_generated": "cover_letter" in state,
            "validation_complete": "validation_result" in state,
            "state_keys": list(state.keys())
        }