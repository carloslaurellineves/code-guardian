"""
Example usage of the Code Guardian orchestrator.
This script demonstrates how to use the LangGraph-based orchestrator for generating unit tests.
"""

import asyncio
import json
from src.orchestrator import TestGenerationOrchestrator
from src.config import config

def main():
    """Main function to demonstrate orchestrator usage."""
    
    # Initialize the orchestrator
    print("🚀 Initializing Code Guardian Orchestrator...")
    orchestrator = TestGenerationOrchestrator()
    
    # Example 1: Text input
    print("\\n📝 Example 1: Text Input")
    sample_python_code = '''
def calculate_factorial(n):
    """Calculate the factorial of a number."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * calculate_factorial(n - 1)

def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
'''
    
    try:
        result = orchestrator.generate_tests_from_text(sample_python_code)
        print(f"✅ Text processing result: {result['success']}")
        if result['success']:
            print(f"   Language detected: {result['detected_language']}")
            print(f"   Test framework: {result['test_framework']}")
            print(f"   Generated tests preview: {result['generated_tests'][:200]}...")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Text processing failed: {e}")
    
    # Example 2: File input (create a temporary file)
    print("\\n📄 Example 2: File Input")
    test_file_path = "temp_example.py"
    
    try:
        # Create a temporary file
        with open(test_file_path, 'w') as f:
            f.write(sample_python_code)
        
        result = orchestrator.generate_tests_from_file(test_file_path)
        print(f"✅ File processing result: {result['success']}")
        if result['success']:
            print(f"   Language detected: {result['detected_language']}")
            print(f"   Test framework: {result['test_framework']}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ File processing failed: {e}")
    finally:
        # Clean up temporary file
        try:
            import os
            os.remove(test_file_path)
        except:
            pass
    
    # Example 3: GitLab repository (if token is configured)
    print("\\n🔗 Example 3: GitLab Repository")
    if config.GITLAB_TOKEN:
        # Use a public repository as an example
        gitlab_url = "https://gitlab.com/example/public-repo"  # Replace with actual repo
        
        try:
            result = orchestrator.generate_tests_from_gitlab(gitlab_url)
            print(f"✅ GitLab processing result: {result['success']}")
            if result['success']:
                print(f"   Language detected: {result['detected_language']}")
                print(f"   Test framework: {result['test_framework']}")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ GitLab processing failed: {e}")
    else:
        print("⚠️  GitLab token not configured. Skipping GitLab example.")
    
    # Display workflow visualization
    print("\\n🔄 Workflow Visualization:")
    try:
        mermaid_diagram = orchestrator.get_workflow_visualization()
        print(mermaid_diagram)
    except Exception as e:
        print(f"Failed to generate workflow visualization: {e}")

def validate_configuration():
    """Validate that the required configuration is present."""
    print("🔧 Validating configuration...")
    
    try:
        config.validate_required_settings()
        print("✅ Configuration is valid!")
        return True
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\\n📋 Please ensure you have:")
        print("   1. Created a .env file from .env.example")
        print("   2. Set your Azure OpenAI credentials")
        print("   3. (Optional) Set GitLab token for repository access")
        return False

def test_individual_components():
    """Test individual components of the system."""
    print("\\n🧪 Testing Individual Components...")
    
    # Test GitLab service
    print("\\n🔗 Testing GitLab Service...")
    try:
        from src.services import GitLabService
        gitlab_service = GitLabService()
        
        if gitlab_service.test_connection():
            print("✅ GitLab service connection successful")
        else:
            print("⚠️  GitLab service connection failed (may be expected without token)")
    except Exception as e:
        print(f"❌ GitLab service test failed: {e}")
    
    # Test LLM chain
    print("\\n🤖 Testing LLM Chain...")
    try:
        from src.llm_calls import TestGenerationChain
        
        # This will only work if Azure OpenAI is properly configured
        chain = TestGenerationChain()
        print("✅ LLM chain initialized successfully")
    except Exception as e:
        print(f"❌ LLM chain test failed: {e}")

if __name__ == "__main__":
    print("🧠 Code Guardian - AI-Powered Unit Test Generator")
    print("=" * 50)
    
    # Validate configuration first
    if not validate_configuration():
        exit(1)
    
    # Test individual components
    test_individual_components()
    
    # Run main examples
    main()
    
    print("\\n🎉 Example usage completed!")
    print("\\n💡 Next steps:")
    print("   1. Integrate with FastAPI backend")
    print("   2. Connect to React frontend")
    print("   3. Add Azure AD authentication")
    print("   4. Deploy to corporate infrastructure")
