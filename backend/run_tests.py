#!/usr/bin/env python3
"""
Simple test runner for core features.
"""
import subprocess
import sys
import os


def run_tests():
    """Run the focused unit tests."""
    
    # Change to the backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Set PYTHONPATH for imports
    os.environ['PYTHONPATH'] = os.getcwd()
    
    print("Running focused unit tests for core features...")
    print("=" * 50)
    
    # Run pytest with verbose output
    cmd = ["python", "-m", "pytest", "tests/test_core_features.py", "-v"]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 