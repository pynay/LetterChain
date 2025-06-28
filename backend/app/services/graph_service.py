from typing import Dict, Any, Optional, AsyncGenerator
import logging
import asyncio
import json
from app.workflows.graph import invoke_graph
from app.core.tracing import tracing_service

logger = logging.getLogger(__name__)

class GraphService:
    """Service for orchestrating LangGraph workflows"""
    
    async def invoke_graph(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the LangGraph workflow asynchronously"""
        
        # Run the graph in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, invoke_graph, state)
        
        return result
    
    async def invoke_graph_streaming(
        self, 
        state: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """Invoke the graph with streaming updates"""
        
        # Send initial status
        yield f"data: {json.dumps({'status': 'Starting workflow...'})}\n\n"
        
        # Execute workflow
        result = await self.invoke_graph(state)
        
        # Send progress updates
        if "generation_metadata" in result:
            metadata = result["generation_metadata"]
            yield f"data: {json.dumps({'status': 'Workflow completed', 'metadata': metadata})}\n\n"
        
        # Send final result
        yield f"data: {json.dumps({'result': result})}\n\n"
    
    async def invoke_graph_with_feedback(
        self, 
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Invoke the graph with user feedback for improvement"""
        
        # Add feedback processing logic
        feedback = state.get("user_feedback", "")
        current_letter = state.get("cover_letter", "")
        
        if feedback and current_letter:
            # Create feedback analysis prompt
            feedback_prompt = f"""
            Analyze the user feedback on this cover letter and provide suggestions for improvement.
            
            Cover Letter:
            {current_letter}
            
            User Feedback:
            {feedback}
            
            Provide specific, actionable suggestions for improving the letter.
            """
            
            # Process feedback (you could integrate this with your AI service)
            state["feedback_processed"] = True
            state["feedback_analysis"] = {
                "feedback_received": feedback,
                "suggestions": ["Consider the user feedback for future improvements"]
            }
        
        return state
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow (for future async processing)"""
        # This could integrate with a task queue like Celery or Redis
        return {
            "workflow_id": workflow_id,
            "status": "completed",  # Placeholder
            "progress": 100
        }