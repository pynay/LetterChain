from typing import Dict, Any, Optional, AsyncGenerator
import logging
import asyncio
import json
from app.workflows.graph import invoke_graph
from app.core.tracing import tracing_service
from app.workflows.nodes import (
    input_validation_node,
    resume_parser_node,
    job_parser_node,
    relevance_matcher_node,
    cover_letter_generator_node,
    cover_letter_validator_node
)

logger = logging.getLogger(__name__)

class GraphService:
    """Service for orchestrating LangGraph workflows"""
    
    async def invoke_graph(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the LangGraph workflow asynchronously"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, invoke_graph, state)
        return result
    
    async def invoke_graph_streaming(
        self, 
        state: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """Invoke the graph with streaming updates"""
        # 1. Input validation
        yield f"data: {json.dumps({'status': 'Validating input...'})}\n\n"
        state = await asyncio.get_event_loop().run_in_executor(None, input_validation_node, state)
        if state.get("validation_failed", False):
            yield f"data: {json.dumps({'status': 'Input validation failed', 'error': state.get('validation_error', {})})}\n\n"
            yield f"data: ERROR::Input validation failed\n\n"
            yield "data: done\n\n"
            return
        # 2. Parsing resume
        yield f"data: {json.dumps({'status': 'Parsing resume...'})}\n\n"
        state = await asyncio.get_event_loop().run_in_executor(None, resume_parser_node, state)
        # 3. Parsing job description
        yield f"data: {json.dumps({'status': 'Parsing job description...'})}\n\n"
        state = await asyncio.get_event_loop().run_in_executor(None, job_parser_node, state)
        # 4. Matching experiences
        yield f"data: {json.dumps({'status': 'Matching experiences...'})}\n\n"
        state = await asyncio.get_event_loop().run_in_executor(None, relevance_matcher_node, state)
        # 5. Generating cover letter
        yield f"data: {json.dumps({'status': 'Generating cover letter...'})}\n\n"
        state = await asyncio.get_event_loop().run_in_executor(None, cover_letter_generator_node, state)
        # 6. Validating output
        yield f"data: {json.dumps({'status': 'Validating output...'})}\n\n"
        state = await asyncio.get_event_loop().run_in_executor(None, cover_letter_validator_node, state)
        # 7. Workflow completed
        yield f"data: {json.dumps({'status': 'Workflow completed'})}\n\n"
        # 8. Final result
        if "cover_letter" in state:
            yield f"data: FINAL_COVER_LETTER::{json.dumps({'cover_letter': state['cover_letter']})}\n\n"
            yield "data: done\n\n"
        elif "error" in state:
            error_detail = state["error"].get("details", "Unknown error")
            yield f"data: ERROR::{error_detail}\n\n"
            yield "data: done\n\n"
        else:
            yield f"data: {json.dumps(state)}\n\n"
            yield "data: done\n\n"
    
    async def invoke_graph_with_feedback(
        self, 
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Invoke the graph with user feedback for improvement"""
        feedback = state.get("user_feedback", "")
        current_letter = state.get("cover_letter", "")
        if feedback and current_letter:
            feedback_prompt = f"""
            Analyze the user feedback on this cover letter and provide suggestions for improvement.
            Cover Letter:
            {current_letter}
            User Feedback:
            {feedback}
            Provide specific, actionable suggestions for improving the letter.
            """
            state["feedback_processed"] = True
            state["feedback_analysis"] = {
                "feedback_received": feedback,
                "suggestions": ["Consider the user feedback for future improvements"]
            }
        return state
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow (for future async processing)"""
        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "progress": 100
        }