#!/usr/bin/env python3
"""
Simple test script to verify the new backend structure works.
Run this to check if all imports and basic functionality work.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported successfully"""
    print("Testing imports...")
    
    try:
        # Test core modules
        from app.core.config import settings
        print("✅ Core config imported")
        
        from app.core.tracing import tracing_service
        print("✅ Tracing service imported")
        
        # Test services
        from app.services.ai_service import ai_service
        print("✅ AI service imported")
        
        from app.services.cache_service import cache_service
        print("✅ Cache service imported")
        
        from app.services.file_service import file_service
        print("✅ File service imported")
        
        from app.services.graph_service import GraphService
        print("✅ Graph service imported")
        
        # Test models
        from app.models.schemas import CoverLetterRequest, CoverLetterResponse
        print("✅ Schemas imported")
        
        # Test workflows
        from app.workflows.state import CoverLetterState
        print("✅ State imported")
        
        from app.workflows.nodes import input_validation_node
        print("✅ Nodes imported")
        
        from app.workflows.graph import app_graph
        print("✅ Graph imported")
        
        # Test API
        from app.api.routes import router
        print("✅ API routes imported")
        
        from app.api.middleware import setup_middleware
        print("✅ Middleware imported")
        
        # Test main app
        from main import create_app
        print("✅ Main app imported")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def test_app_creation():
    """Test that the FastAPI app can be created"""
    print("\nTesting app creation...")
    
    try:
        from main import create_app
        app = create_app()
        print("✅ FastAPI app created successfully")
        print(f"   Title: {app.title}")
        print(f"   Version: {app.version}")
        return True
        
    except Exception as e:
        print(f"❌ App creation failed: {str(e)}")
        return False

def test_services():
    """Test that services can be instantiated"""
    print("\nTesting services...")
    
    try:
        from app.services.ai_service import ai_service
        from app.services.cache_service import cache_service
        from app.services.file_service import file_service
        from app.services.graph_service import GraphService
        
        # Test AI service
        models = ai_service.models
        print(f"✅ AI service initialized with {len(models)} models")
        
        # Test cache service (will fail if Redis is not running, but that's expected)
        try:
            cache_service._test_connection()
            print("✅ Cache service connected to Redis")
        except Exception as e:
            print(f"⚠️  Cache service: Redis not available ({str(e)})")
        
        # Test file service
        print("✅ File service initialized")
        
        # Test graph service
        graph_service = GraphService()
        print("✅ Graph service initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Service test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing New Backend Structure")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_app_creation,
        test_services
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your new backend is ready.")
        print("\nNext steps:")
        print("1. Create a .env file with your configuration")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Start Redis server")
        print("4. Run the server: python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 