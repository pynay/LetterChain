from langfuse import get_client
from functools import wraps
import time
import logging
from typing import Optional, Dict, Any, Callable
from .config import settings

logger = logging.getLogger(__name__)

class TracingService:
    """Centralized tracing service for Langfuse integration"""

    def __init__(self):
        if settings.ENABLE_TRACING:
            self.langfuse = get_client()
        else:
            self.langfuse = None

    def trace_node(self, node_name: str) -> Callable:
        """Decorator to trace LangGraph nodes with detailed metrics"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(state: dict) -> dict:
                if not self.langfuse:
                    return func(state)
                
                metadata = self._extract_state_metadata(state)
                start_time = time.time()
                
                with self.langfuse.start_as_current_span(name=f"langgraph_node_{node_name}") as span:
                    span.update_trace(metadata=metadata)
                    try:
                        result = func(state)
                        execution_time = time.time() - start_time
                        span.update_trace(metadata={
                            **metadata,
                            "execution_time_ms": round(execution_time * 1000, 2),
                            "output_keys": list(result.keys()),
                            "state_size": len(str(result))
                        })
                        return result
                    except Exception as e:
                        execution_time = time.time() - start_time
                        logger.error(f"Node {node_name} failed: {str(e)}")
                        span.update_trace(metadata={
                            **metadata,
                            "execution_time_ms": round(execution_time * 1000, 2),
                            "error": str(e)
                        })
                        raise
            return wrapper
        return decorator

    def trace_api_request(self, endpoint_name: str) -> Callable:
        """Decorator to trace API endpoints with request/response data"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                if not self.langfuse:
                    return await func(*args, **kwargs)
                
                start_time = time.time()
                
                with self.langfuse.start_as_current_span(name=f"api_{endpoint_name}") as span:
                    span.update_trace(metadata={
                        "endpoint": endpoint_name,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys())
                    })
                    try:
                        result = await func(*args, **kwargs)
                        execution_time = time.time() - start_time
                        span.update_trace(metadata={
                            "execution_time_ms": round(execution_time * 1000, 2),
                            "result_type": type(result).__name__
                        })
                        return result
                    except Exception as e:
                        execution_time = time.time() - start_time
                        logger.error(f"API {endpoint_name} failed: {str(e)}")
                        span.update_trace(metadata={
                            "execution_time_ms": round(execution_time * 1000, 2),
                            "error": str(e)
                        })
                        raise
            return wrapper
        return decorator

    def log_ai_generation(
        self,
        model_name: str,
        prompt: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log AI model generations with detailed metrics"""
        if not self.langfuse:
            return
        # You can use a span or generation here if you want more detail
        # For now, just log as a span
        with self.langfuse.start_as_current_span(name=f"ai_generation_{model_name}") as span:
            span.update_trace(metadata={
                "model": model_name,
                "prompt_length": len(prompt),
                "response_length": len(response),
                "tokens_estimated": len(prompt.split()) + len(response.split()),
                **(metadata or {})
            })

    def _extract_state_metadata(self, state: dict) -> Dict[str, Any]:
        """Extract relevant metadata from LangGraph state"""
        return {
            "job_title": state.get("job_info", {}).get("title", "Unknown"),
            "company": state.get("job_info", {}).get("company", "Unknown"),
            "user_name": state.get("user_name", "Unknown"),
            "has_resume_info": "resume_info" in state,
            "has_job_info": "job_info" in state,
            "matched_experiences_count": len(state.get("matched_experiences", [])),
            "state_keys": list(state.keys())
        }

# Global tracing service instance
tracing_service = TracingService()
