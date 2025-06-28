from langchain_anthropic import ChatAnthropic
from typing import Dict, Any, Optional
import time
import random
import logging
from app.core.config import settings
from app.core.tracing import tracing_service
import asyncio

logger = logging.getLogger(__name__)

class AIService:
    """Centralized AI model management with retry logic and tracing"""
    def __init__(self):
        self.models: Dict[str, ChatAnthropic] = {}
        self._initialize_models()

    
    def _initialize_models(self):
        """Initialize all AI models with appropriate configurations"""
        model_configs = {
            "claude-3-5-haiku": {
                "model": "claude-3-5-haiku-20241022",
                "temperature": 0.0,
                "max_tokens": 256
            },
            "claude-3-7-sonnet": {
                "model": "claude-3-7-sonnet-20250219",
                "temperature": 0.2,
                "max_tokens": 1024
            },
            "claude-opus-4": {
                "model": "claude-opus-4-20250514",
                "temperature": 0.6,
                "max_tokens": 1024
            }
        }


        #Abstract model bodies
        for name, config in model_configs.items():
            self.models[name] = ChatAnthropic(
                model=config["model"],
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
                temperature=config["temperature"],
                max_tokens=config["max_tokens"]
            )

    def get_model(self, model_name: str) -> ChatAnthropic:
        """Get a specific AI model by name"""
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        return self.models[model_name]
    
    def invoke_with_retry(
        self,
        model_name: str,
        prompt: str,
        max_retries: int = 3,
        base_delay: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Synchronous version of invoke_with_retry for LangGraph nodes"""
        model = self.get_model(model_name)

        for attempt in range(max_retries):
            try:
                start_time = time.time()

                response = model.invoke(prompt)
                response_text = response.content

                execution_time = time.time() - start_time

                # Log the AI generation using Langfuse
                tracing_service.log_ai_generation(
                    model_name=model_name,
                    prompt=prompt,
                    response=response_text,
                    metadata={
                        "attempt": attempt + 1,
                        "execution_time_ms": round(execution_time * 1000, 2),
                        **(metadata or {})
                    }
                )

                logger.info(f"AI generation successful: {model_name} (attempt {attempt + 1})")
                return response_text
            
            except Exception as e:
                error_msg = str(e).lower()

                should_retry = (
                    "529" in str(e) or 
                    "rate limit" in error_msg or
                    "timeout" in error_msg
                )
                if not should_retry or attempt == max_retries - 1:
                    logger.error(f"AI generation failed: {model_name} - {str(e)}")
                    raise
                
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"AI generation retry {attempt + 1}/{max_retries}")
                time.sleep(delay)  # Use time.sleep instead of asyncio.sleep
        raise Exception(f"Max retries exceeded for {model_name}")
    
    async def invoke_with_retry_async(
        self,
        model_name: str,
        prompt: str,
        max_retries: int = 3,
        base_delay: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Async version of invoke_with_retry for API endpoints"""
        model = self.get_model(model_name)

        for attempt in range(max_retries):
            try:
                start_time = time.time()

                response = model.invoke(prompt)
                response_text = response.content

                execution_time = time.time() - start_time

                # Log the AI generation using Langfuse
                tracing_service.log_ai_generation(
                    model_name=model_name,
                    prompt=prompt,
                    response=response_text,
                    metadata={
                        "attempt": attempt + 1,
                        "execution_time_ms": round(execution_time * 1000, 2),
                        **(metadata or {})
                    }
                )

                logger.info(f"AI generation successful: {model_name} (attempt {attempt + 1})")
                return response_text
            
            except Exception as e:
                error_msg = str(e).lower()

                should_retry = (
                    "529" in str(e) or 
                    "rate limit" in error_msg or
                    "timeout" in error_msg
                )
                if not should_retry or attempt == max_retries - 1:
                    logger.error(f"AI generation failed: {model_name} - {str(e)}")
                    raise
                
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"AI generation retry {attempt + 1}/{max_retries}")
                await asyncio.sleep(delay)
        raise Exception(f"Max retries exceeded for {model_name}")
    
    def create_system_prompt(self, role: str, instructions: str) -> str:
        """Create a standardized system prompt"""
        return f"""You are {role}.

{instructions}

You must respond with only the requested information. Do not include any explanations, markdown formatting, or additional text unless specifically requested."""
    
    def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """Synchronous version of parse_resume for LangGraph nodes"""
        system_prompt = self.create_system_prompt(
            role="a professional resume parser",
            instructions="""Extract structured information from the resume. Return ONLY a JSON object with:
- name: string
- email: string (if found)
- phone: string (if found)
- experience: array of objects with title, company, duration, description
- education: array of objects with degree, institution, year
- skills: array of strings
- summary: string (if available)"""
        )

        prompt = f"{system_prompt}\n\nResume:\n{resume_text}"

        response = self.invoke_with_retry(
            model_name="claude-3-7-sonnet",
            prompt=prompt,
            metadata={"operation": "resume_parsing"}
        )

        return self._parse_json_response(response)
    
    def parse_job(self, job_text: str) -> Dict[str, Any]:
        """Synchronous version of parse_job for LangGraph nodes"""
        system_prompt = self.create_system_prompt(
            role="a professional job description parser",
            instructions="""Extract structured information from the job posting. Return ONLY a JSON object with:
- title: string
- company: string
- location: string (if found)
- requirements: array of strings
- responsibilities: array of strings
- qualifications: array of strings"""
        )

        prompt = f"{system_prompt}\n\nJob Description:\n{job_text}"

        response = self.invoke_with_retry(
            model_name="claude-3-7-sonnet",
            prompt=prompt,
            metadata={"operation": "job_parsing"}
        )

        return self._parse_json_response(response)
    
    async def parse_resume_async(self, resume_text: str) -> Dict[str, Any]:
        """Async version of parse_resume for API endpoints"""
        system_prompt = self.create_system_prompt(
            role="a professional resume parser",
            instructions="""Extract structured information from the resume. Return ONLY a JSON object with:
- name: string
- email: string (if found)
- phone: string (if found)
- experience: array of objects with title, company, duration, description
- education: array of objects with degree, institution, year
- skills: array of strings
- summary: string (if available)"""
        )

        prompt = f"{system_prompt}\n\nResume:\n{resume_text}"

        response = await self.invoke_with_retry_async(
            model_name="claude-3-7-sonnet",
            prompt=prompt,
            metadata={"operation": "resume_parsing"}
        )

        return self._parse_json_response(response)
    
    async def parse_job_async(self, job_text: str) -> Dict[str, Any]:
        """Async version of parse_job for API endpoints"""
        system_prompt = self.create_system_prompt(
            role="a professional job description parser",
            instructions="""Extract structured information from the job posting. Return ONLY a JSON object with:
- title: string
- company: string
- location: string (if found)
- requirements: array of strings
- responsibilities: array of strings
- qualifications: array of strings"""
        )

        prompt = f"{system_prompt}\n\nJob Description:\n{job_text}"

        response = await self.invoke_with_retry_async(
            model_name="claude-3-7-sonnet",
            prompt=prompt,
            metadata={"operation": "job_parsing"}
        )

        return self._parse_json_response(response)

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from AI response with error handling"""
        import json
        import re

        json_match = re.search(r"```(?:json)?\n?(.*?)\n?```", response, re.DOTALL)

        if json_match:
            json_str=json_match.group(1).strip()
        else:
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError("No valid JSON found in response")
            
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {json_str}")
            raise ValueError(f"Invalid JSON response: {str(e)}")
        
ai_service = AIService()