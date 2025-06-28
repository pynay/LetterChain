from langfuse import Langfuse
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
            self.langfuse = Langfuse(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_HOST
            )
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
                
                with self.langfuse.trace(
                    name=f"langgraph_node_{node_name}",
                    metadata={
                        "node_name": node_name,
                        **metadata
                    }
                ) as trace:
                    try:
                        result = func(state)
                        execution_time = time.time() - start_time
                        
                        trace.update(
                            status="success",
                            metadata={
                                **metadata,
                                "execution_time_ms": round(execution_time * 1000, 2),
                                "output_keys": list(result.keys()),
                                "state_size": len(str(result))
                            }
                        )
                        return result
                    except Exception as e:
                        execution_time = time.time() - start_time
                        logger.error(f"Node {node_name} failed: {str(e)}")
                        trace.update(
                            status="error",
                            error=str(e),
                            metadata={
                                **metadata,
                                "execution_time_ms": round(execution_time * 1000, 2)
                            }
                        )
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
                
                with self.langfuse.trace(
                    name=f"api_{endpoint_name}",
                    metadata={
                        "endpoint": endpoint_name,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys())
                    }
                ) as trace:
                    try:
                        result = await func(*args, **kwargs)
                        execution_time = time.time() - start_time
                        
                        trace.update(
                            status="success",
                            metadata={
                                "execution_time_ms": round(execution_time * 1000, 2),
                                "result_type": type(result).__name__
                            }
                        )
                        
                        return result
                    except Exception as e:
                        execution_time = time.time() - start_time
                        logger.error(f"API {endpoint_name} failed: {str(e)}")
                        
                        trace.update(
                            status="error",
                            error=str(e),
                            metadata={
                                "execution_time_ms": round(execution_time * 1000, 2)
                            }
                        )
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
        
        self.langfuse.generation(
            name=f"ai_generation_{model_name}",
            model=model_name,
            prompt=prompt,
            completion=response,
            metadata={
                "prompt_length": len(prompt),
                "response_length": len(response),
                "tokens_estimated": len(prompt.split()) + len(response.split()),
                **(metadata or {})
            }
        )

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
