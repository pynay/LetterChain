from langgraph.graph import StateGraph
from typing import Dict, Any
import logging
from .state import CoverLetterState, StateValidator
from .nodes import (
    input_validation_node,
    resume_parser_node,
    job_parser_node,
    relevance_matcher_node,
    cover_letter_generator_node,
    cover_letter_validator_node
)

logger = logging.getLogger(__name__)

def create_cover_letter_graph() -> StateGraph:
    """Create and configure the LangGraph workflow for cover letter generation"""
    
    # Initialize the graph with our state type
    graph = StateGraph(CoverLetterState)
    
    # Add all nodes to the graph
    graph.add_node("validate_input", input_validation_node)
    graph.add_node("parse_resume", resume_parser_node)
    graph.add_node("parse_job", job_parser_node)
    graph.add_node("match_experiences", relevance_matcher_node)
    graph.add_node("generate_letter", cover_letter_generator_node)
    graph.add_node("validate_letter", cover_letter_validator_node)
    
    # Add error handling and finish nodes
    graph.add_node("error_handler", error_handler_node)
    graph.add_node("finish", finish_node)
    
    # Set the entry point
    graph.set_entry_point("validate_input")
    
    # Define conditional routing functions
    def input_validation_branch(state: Dict[str, Any]) -> str:
        """Route based on input validation results"""
        if state.get("validation_failed", False):
            return "error_handler"
        return "parse_resume"
    
    def parsing_branch(state: Dict[str, Any]) -> str:
        """Route after parsing is complete"""
        # Both resume and job should be parsed by now
        if "resume_info" in state and "job_info" in state:
            return "parse_job"  # Continue to job parsing
        return "error_handler"
    
    def job_parsing_branch(state: Dict[str, Any]) -> str:
        """Route after job parsing"""
        if "job_info" in state:
            return "match_experiences"
        return "error_handler"
    
    def matching_branch(state: Dict[str, Any]) -> str:
        """Route after experience matching"""
        if "matched_experiences" in state:
            return "generate_letter"
        return "error_handler"
    
    def validation_branch(state: Dict[str, Any]) -> str:
        """Route based on cover letter validation results"""
        validation_result = state.get("validation_result", {})
        
        if validation_result.get("valid", False):
            # Letter is valid, we're done
            return "finish"
        else:
            # Letter needs revision, try again
            # Check if we've tried too many times
            prior_issues = state.get("prior_issues", [])
            if len(prior_issues) >= 3:  # Max 3 attempts
                logger.warning("Max validation attempts reached")
                return "finish"
            return "generate_letter"
    
    # Add conditional edges
    graph.add_conditional_edges(
        "validate_input",
        input_validation_branch,
        {
            "error_handler": "error_handler",
            "parse_resume": "parse_resume"
        }
    )
    
    graph.add_conditional_edges(
        "parse_resume",
        parsing_branch,
        {
            "parse_job": "parse_job",
            "error_handler": "error_handler"
        }
    )
    
    graph.add_conditional_edges(
        "parse_job",
        job_parsing_branch,
        {
            "match_experiences": "match_experiences",
            "error_handler": "error_handler"
        }
    )
    
    graph.add_conditional_edges(
        "match_experiences",
        matching_branch,
        {
            "generate_letter": "generate_letter",
            "error_handler": "error_handler"
        }
    )
    
    graph.add_conditional_edges(
        "validate_letter",
        validation_branch,
        {
            "finish": "finish",
            "generate_letter": "generate_letter"
        }
    )
    
    # Add regular edges for sequential flow
    graph.add_edge("generate_letter", "validate_letter")
    
    # Set finish points
    graph.set_finish_point("finish")
    graph.set_finish_point("error_handler")
    
    return graph.compile()

def error_handler_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle errors in the workflow"""
    logger.error("Workflow error occurred", extra={"state": StateValidator.get_state_summary(state)})
    
    # Add error information to state
    state["error"] = {
        "message": "Workflow execution failed",
        "validation_failed": state.get("validation_failed", False),
        "validation_error": state.get("validation_error", {}),
        "state_summary": StateValidator.get_state_summary(state)
    }
    
    return state

def finish_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Final node that marks successful completion"""
    logger.info("Workflow completed successfully", extra={"state": StateValidator.get_state_summary(state)})
    
    # Add completion metadata
    state["workflow_completed"] = True
    state["status"] = "success"
    
    return state

# Create the compiled graph instance
app_graph = create_cover_letter_graph()

def invoke_graph(state: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke the graph with proper error handling and logging"""
    try:
        # Validate initial state
        if not StateValidator.validate_initial_state(state):
            raise ValueError("Invalid initial state")
        
        logger.info("Starting cover letter generation workflow", 
                   extra={"state_summary": StateValidator.get_state_summary(state)})
        
        # Invoke the graph
        result = app_graph.invoke(state)
        
        # Add generation metadata
        result["generation_metadata"] = {
            "workflow_completed": True,
            "final_state_summary": StateValidator.get_state_summary(result),
            "has_error": "error" in result
        }
        
        logger.info("Cover letter generation workflow completed",
                   extra={"result_summary": result.get("generation_metadata")})
        
        return result
        
    except Exception as e:
        logger.error(f"Graph invocation failed: {str(e)}")
        return {
            "error": {
                "message": "Workflow execution failed",
                "details": str(e)
            },
            "generation_metadata": {
                "workflow_completed": False,
                "error": str(e)
            }
        }