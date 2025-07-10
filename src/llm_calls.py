"""
LangChain-based client for interacting with Azure OpenAI for test generation.
"""

from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain.chains import LLMChain
from typing import Dict, Any, Optional
import logging

from src.config import config
from src.models import TestGenerationResult

logger = logging.getLogger(__name__)


class TestGenerationChain:
    """LangChain-based chain for generating unit tests using Azure OpenAI."""

    def __init__(self):
        """Initialize the test generation chain."""
        self.llm = self._initialize_llm()
        self.prompt_template = self._create_prompt_template()
        self.chain = self._create_chain()

    def _initialize_llm(self) -> AzureChatOpenAI:
        """Initialize the Azure OpenAI LLM instance."""
        try:
            return AzureChatOpenAI(
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
                api_key=config.AZURE_OPENAI_API_KEY,
                api_version=config.AZURE_OPENAI_API_VERSION,
                deployment_name=config.AZURE_OPENAI_DEPLOYMENT_NAME,
                temperature=0.1,  # Low temperature for consistent test generation
                max_tokens=2000,
                timeout=30
            )
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            raise

    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Create the prompt template for test generation."""
        system_template = """
You are an expert software engineer specialized in creating comprehensive unit tests.
Your task is to analyze the provided source code and generate high-quality unit tests.

Guidelines:
1. Generate complete, runnable unit tests
2. Cover edge cases and error scenarios
3. Use appropriate testing frameworks for the detected language
4. Include setup and teardown methods if needed
5. Add descriptive test method names and docstrings
6. Ensure tests are independent and can run in any order
7. Mock external dependencies appropriately

Languages and Frameworks:
- Python: Use pytest or unittest
- Java: Use JUnit 5
- JavaScript/TypeScript: Use Jest or Mocha
- C#: Use NUnit or MSTest
- Go: Use standard testing package
- Other languages: Use the most common testing framework

Provide only the test code without explanation unless specifically requested.
"""

        human_template = """
Please generate comprehensive unit tests for the following code:

Programming Language: {language}
Input Type: {input_type}

Source Code:
```{language}
{code}
```

Additional Context: {context}

Generate unit tests that cover:
1. Normal operation scenarios
2. Edge cases
3. Error handling
4. Input validation
5. Boundary conditions
"""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])

    def _create_chain(self) -> LLMChain:
        """Create the LangChain chain for test generation."""
        return LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            output_parser=StrOutputParser(),
            verbose=True
        )

    def generate_tests(
        self, 
        code: str, 
        language: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> TestGenerationResult:
        """Generate unit tests for the provided code."""
        try:
            # Prepare input for the chain
            chain_input = {
                "code": code,
                "language": language or "unknown",
                "input_type": context.get("input_type", "unknown") if context else "unknown",
                "context": str(context) if context else "No additional context"
            }
            
            logger.info(f"Generating tests for {language} code")
            
            # Generate tests using the chain
            generated_test_code = self.chain.run(chain_input)
            
            # Determine appropriate test framework
            framework = self._determine_test_framework(language)
            
            # Generate coverage notes
            coverage_notes = self._generate_coverage_notes(code, language)
            
            return TestGenerationResult(
                test_code=generated_test_code,
                framework=framework,
                coverage_notes=coverage_notes,
                language=language,
                confidence_score=0.85,  # Placeholder confidence score
                suggestions=[
                    "Review generated tests for completeness",
                    "Add integration tests if needed",
                    "Consider performance testing for critical paths"
                ]
            )
            
        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            raise

    def _determine_test_framework(self, language: str) -> str:
        """Determine the appropriate test framework for the language."""
        framework_mapping = {
            "python": "pytest",
            "java": "JUnit 5",
            "javascript": "Jest",
            "typescript": "Jest",
            "c#": "NUnit",
            "go": "testing",
            "rust": "cargo test",
            "php": "PHPUnit",
            "ruby": "RSpec",
            "swift": "XCTest",
            "kotlin": "JUnit 5",
            "scala": "ScalaTest"
        }
        
        return framework_mapping.get(language.lower(), "framework-specific")

    def _generate_coverage_notes(self, code: str, language: str) -> str:
        """Generate notes about test coverage."""
        # Analyze code complexity and suggest coverage areas
        lines_of_code = len(code.split('\n'))
        
        if lines_of_code < 50:
            complexity = "low"
        elif lines_of_code < 200:
            complexity = "medium"
        else:
            complexity = "high"
            
        return f"""
Test Coverage Analysis:
- Code complexity: {complexity}
- Lines of code: {lines_of_code}
- Recommended coverage: >= 85%
- Focus areas: Error handling, edge cases, integration points
- Consider adding performance tests for critical methods
"""


class OpenAIClient:
    """Simplified client interface for backward compatibility."""

    def __init__(self, api_key: str = None, endpoint: str = None, version: str = None, deployment_name: str = None):
        """Initialize with optional parameters for compatibility."""
        self.test_chain = TestGenerationChain()

    def generate_tests(self, code_content: str, language: str = "python") -> str:
        """Generate unit tests from the code content using LLM."""
        try:
            result = self.test_chain.generate_tests(
                code=code_content,
                language=language
            )
            return result.test_code
        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            return f"# Error generating tests: {e}\n# Original code:\n{code_content}"

