"""
Focused unit tests for core features.
"""
import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add the app directory to the path for imports
sys.path.insert(0, os.path.abspath('.'))


class TestFileService:
    """Test core file processing functionality."""
    
    def test_validate_upload_valid_pdf(self):
        """Test that valid PDF files are accepted."""
        from app.services.file_service import FileService
        from fastapi import UploadFile
        
        with patch('app.services.file_service.settings') as mock_settings:
            mock_settings.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
            mock_settings.ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt']
            mock_settings.ALLOWED_MIME_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
            
            mock_file = MagicMock(spec=UploadFile)
            mock_file.filename = "resume.pdf"
            mock_file.content_type = "application/pdf"
            
            file_bytes = b"test content" * 1000  # Small file
            
            result = FileService.validate_upload(mock_file, file_bytes, "resume")
            
            assert result.is_valid is True
            assert result.filename == "resume.pdf"
            assert result.error_message is None

    def test_validate_upload_file_too_large(self):
        """Test that oversized files are rejected."""
        from app.services.file_service import FileService
        from fastapi import UploadFile
        
        with patch('app.services.file_service.settings') as mock_settings:
            mock_settings.MAX_FILE_SIZE = 1024  # 1KB
            mock_settings.ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt']
            mock_settings.ALLOWED_MIME_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
            
            mock_file = MagicMock(spec=UploadFile)
            mock_file.filename = "resume.pdf"
            mock_file.content_type = "application/pdf"
            
            file_bytes = b"test content" * 10000  # Large file
            
            result = FileService.validate_upload(mock_file, file_bytes, "resume")
            
            assert result.is_valid is False
            assert "too large" in result.error_message

    def test_generate_file_hash(self):
        """Test file hash generation for caching."""
        from app.services.file_service import FileService
        
        content = "test content"
        result = FileService.generate_file_hash(content)
        
        # Should be a valid SHA-256 hash (64 hex characters)
        assert len(result) == 64
        assert all(c in '0123456789abcdef' for c in result)


class TestCacheService:
    """Test core caching functionality."""
    
    def test_generate_cache_key(self):
        """Test cache key generation."""
        from app.services.cache_service import CacheService
        
        with patch('app.services.cache_service.settings') as mock_settings:
            mock_settings.REDIS_URL = "redis://localhost:6379"
            
            with patch('redis.from_url') as mock_redis_from_url:
                mock_redis_client = MagicMock()
                mock_redis_client.ping.return_value = True
                mock_redis_from_url.return_value = mock_redis_client
                
                cache_service = CacheService()
                
                content = "test content"
                result = cache_service._generate_key("resume", content)
                
                # Should start with prefix and contain hash
                assert result.startswith("resume:")
                assert len(result) > 10

    def test_cache_get_set_operations(self):
        """Test basic cache get/set operations."""
        from app.services.cache_service import CacheService
        
        with patch('app.services.cache_service.settings') as mock_settings:
            mock_settings.REDIS_URL = "redis://localhost:6379"
            
            with patch('redis.from_url') as mock_redis_from_url:
                mock_redis_client = MagicMock()
                mock_redis_client.ping.return_value = True
                mock_redis_from_url.return_value = mock_redis_client
                
                cache_service = CacheService()
                
                # Test set operation
                test_data = {"name": "John", "age": 30}
                mock_redis_client.setex.return_value = True
                
                result = cache_service.set("test-key", test_data)
                assert result is True
                
                # Test get operation
                mock_redis_client.get.return_value = json.dumps(test_data)
                result = cache_service.get("test-key")
                assert result == test_data


class TestAIService:
    """Test core AI functionality."""
    
    def test_create_system_prompt(self):
        """Test system prompt creation."""
        from app.services.ai_service import AIService
        
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            ai_service = AIService()
            
            prompt = ai_service.create_system_prompt("test role", "test instructions")
            
            assert "You are test role" in prompt
            assert "test instructions" in prompt
            assert "You must respond with only the requested information" in prompt

    def test_get_model_valid(self):
        """Test getting a valid model."""
        from app.services.ai_service import AIService
        
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            ai_service = AIService()
            
            model = ai_service.get_model("claude-3-5-haiku")
            assert model is not None

    def test_get_model_invalid(self):
        """Test getting an invalid model raises error."""
        from app.services.ai_service import AIService
        
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            ai_service = AIService()
            
            with pytest.raises(ValueError, match="Unknown model"):
                ai_service.get_model("invalid-model")

    def test_parse_json_response(self):
        """Test JSON response parsing."""
        from app.services.ai_service import AIService
        
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            ai_service = AIService()
            
            # Test valid JSON
            valid_json = '{"name": "John", "age": 30}'
            result = ai_service._parse_json_response(valid_json)
            assert result["name"] == "John"
            assert result["age"] == 30
            
            # Test JSON with code blocks
            json_with_blocks = '```json\n{"name": "John", "age": 30}\n```'
            result = ai_service._parse_json_response(json_with_blocks)
            assert result["name"] == "John"
            assert result["age"] == 30


class TestGraphService:
    """Test core workflow functionality."""
    
    def test_get_workflow_status(self):
        """Test workflow status retrieval."""
        from app.services.graph_service import GraphService
        
        graph_service = GraphService()
        
        workflow_id = "test-workflow-123"
        result = graph_service.get_workflow_status(workflow_id)
        
        assert result["workflow_id"] == workflow_id
        assert result["status"] == "completed"
        assert result["progress"] == 100

    @pytest.mark.asyncio
    async def test_invoke_graph_with_feedback(self):
        """Test feedback processing."""
        from app.services.graph_service import GraphService
        
        graph_service = GraphService()
        
        test_state = {
            "resume_text": "Test resume",
            "job_description": "Test job",
            "cover_letter": "Current cover letter",
            "user_feedback": "Make it more professional"
        }
        
        result = await graph_service.invoke_graph_with_feedback(test_state)
        
        assert result["feedback_processed"] is True
        assert "feedback_analysis" in result
        assert result["feedback_analysis"]["feedback_received"] == "Make it more professional"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 