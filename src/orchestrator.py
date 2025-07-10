"""
LangGraph-based orchestrator for generating unit test cases using AI.
"""

from typing import Dict, Any, Literal, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from dataclasses import dataclass
import logging

from src.input_handlers import TextHandler, FileHandler, GitLabHandler
from src.llm_calls import TestGenerationChain
from src.models import InputType, ProcessingState, TestGenerationResult
from src.config import config

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class TestGenerationOrchestrator:
    """LangGraph-based orchestrator for multi-input unit test generation."""

    def __init__(self):
        """Initialize the orchestrator with LangGraph workflow."""
        self.test_generation_chain = TestGenerationChain()
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for test generation."""
        workflow = StateGraph(ProcessingState)
        
        # Add nodes for each processing step
        workflow.add_node("validate_input", self._validate_input)
        workflow.add_node("process_text", self._process_text_input)
        workflow.add_node("process_file", self._process_file_input)
        workflow.add_node("process_gitlab", self._process_gitlab_input)
        workflow.add_node("generate_tests", self._generate_tests)
        workflow.add_node("format_output", self._format_output)
        
        # Set entry point
        workflow.set_entry_point("validate_input")
        
        # Add conditional edges based on input type
        workflow.add_conditional_edges(
            "validate_input",
            self._route_by_input_type,
            {
                "text": "process_text",
                "file": "process_file",
                "gitlab": "process_gitlab",
                "error": END
            }
        )
        
        # Connect processing nodes to test generation
        workflow.add_edge("process_text", "generate_tests")
        workflow.add_edge("process_file", "generate_tests")
        workflow.add_edge("process_gitlab", "generate_tests")
        
        # Connect test generation to output formatting
        workflow.add_edge("generate_tests", "format_output")
        workflow.add_edge("format_output", END)
        
        return workflow

    def _validate_input(self, state: ProcessingState) -> ProcessingState:
        """Validate the input and determine processing type."""
        logger.info(f"Validating input of type: {state.input_type}")
        
        try:
            if state.input_type == InputType.TEXT:
                if not state.text_input or len(state.text_input.strip()) == 0:
                    raise ValueError("Empty text input provided")
                    
            elif state.input_type == InputType.FILE:
                if not state.file_path:
                    raise ValueError("No file path provided")
                    
            elif state.input_type == InputType.GITLAB:
                if not state.gitlab_url:
                    raise ValueError("No GitLab URL provided")
                    
            else:
                raise ValueError(f"Unsupported input type: {state.input_type}")
                
            state.is_valid = True
            state.messages.append(HumanMessage(content="Input validation successful"))
            
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            state.is_valid = False
            state.error_message = str(e)
            state.messages.append(HumanMessage(content=f"Validation error: {e}"))
            
        return state

    def _route_by_input_type(self, state: ProcessingState) -> str:
        """Route to appropriate processing node based on input type."""
        if not state.is_valid:
            return "error"
            
        routing_map = {
            InputType.TEXT: "text",
            InputType.FILE: "file",
            InputType.GITLAB: "gitlab"
        }
        
        return routing_map.get(state.input_type, "error")

    def _process_text_input(self, state: ProcessingState) -> ProcessingState:
        """Process direct text input."""
        logger.info("Processing text input")
        
        try:
            handler = TextHandler()
            processed_code = handler.process(state.text_input)
            
            state.processed_code = processed_code
            state.detected_language = handler.detect_language(state.text_input)
            state.messages.append(AIMessage(content="Text input processed successfully"))
            
        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            state.error_message = str(e)
            state.messages.append(AIMessage(content=f"Text processing error: {e}"))
            
        return state

    def _process_file_input(self, state: ProcessingState) -> ProcessingState:
        """Process uploaded file input."""
        logger.info(f"Processing file input: {state.file_path}")
        
        try:
            handler = FileHandler()
            processed_code = handler.process(state.file_path)
            
            state.processed_code = processed_code
            state.detected_language = handler.detect_language_from_file(state.file_path)
            state.messages.append(AIMessage(content="File input processed successfully"))
            
        except Exception as e:
            logger.error(f"File processing failed: {e}")
            state.error_message = str(e)
            state.messages.append(AIMessage(content=f"File processing error: {e}"))
            
        return state

    def _process_gitlab_input(self, state: ProcessingState) -> ProcessingState:
        """Process GitLab repository input."""
        logger.info(f"Processing GitLab input: {state.gitlab_url}")
        
        try:
            handler = GitLabHandler()
            processed_code = handler.process(state.gitlab_url)
            
            state.processed_code = processed_code
            state.detected_language = handler.detect_primary_language(processed_code)
            state.messages.append(AIMessage(content="GitLab repository processed successfully"))
            
        except Exception as e:
            logger.error(f"GitLab processing failed: {e}")
            state.error_message = str(e)
            state.messages.append(AIMessage(content=f"GitLab processing error: {e}"))
            
        return state

    def _generate_tests(self, state: ProcessingState) -> ProcessingState:
        """Generate unit tests using LLM."""
        logger.info("Generating unit tests")
        
        try:
            if not state.processed_code:
                raise ValueError("No processed code available for test generation")
                
            # Use LangChain to generate tests
            test_result = self.test_generation_chain.generate_tests(
                code=state.processed_code,
                language=state.detected_language,
                context={"input_type": state.input_type.value}
            )
            
            state.generated_tests = test_result.test_code
            state.test_framework = test_result.framework
            state.coverage_notes = test_result.coverage_notes
            state.messages.append(AIMessage(content="Unit tests generated successfully"))
            
        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            state.error_message = str(e)
            state.messages.append(AIMessage(content=f"Test generation error: {e}"))
            
        return state

    def _format_output(self, state: ProcessingState) -> ProcessingState:
        """Format the final output."""
        logger.info("Formatting output")
        
        try:
            if state.generated_tests:
                # Create structured output
                output = {
                    "success": True,
                    "input_type": state.input_type.value,
                    "detected_language": state.detected_language,
                    "test_framework": state.test_framework,
                    "generated_tests": state.generated_tests,
                    "coverage_notes": state.coverage_notes,
                    "processing_messages": [msg.content for msg in state.messages]
                }
            else:
                output = {
                    "success": False,
                    "error": state.error_message,
                    "processing_messages": [msg.content for msg in state.messages]
                }
                
            state.final_output = output
            state.messages.append(AIMessage(content="Output formatted successfully"))
            
        except Exception as e:
            logger.error(f"Output formatting failed: {e}")
            state.error_message = str(e)
            state.final_output = {
                "success": False,
                "error": str(e)
            }
            
        return state

    def generate_tests_from_text(self, text_input: str) -> Dict[str, Any]:
        """Generate unit tests from direct text input."""
        initial_state = ProcessingState(
            input_type=InputType.TEXT,
            text_input=text_input,
            messages=[]
        )
        
        result = self.app.invoke(initial_state)
        return result.final_output

    def generate_tests_from_file(self, file_path: str) -> Dict[str, Any]:
        """Generate unit tests from uploaded file."""
        initial_state = ProcessingState(
            input_type=InputType.FILE,
            file_path=file_path,
            messages=[]
        )
        
        result = self.app.invoke(initial_state)
        return result.final_output

    def generate_tests_from_gitlab(self, gitlab_url: str) -> Dict[str, Any]:
        """Generate unit tests from GitLab repository."""
        initial_state = ProcessingState(
            input_type=InputType.GITLAB,
            gitlab_url=gitlab_url,
            messages=[]
        )
        
        result = self.app.invoke(initial_state)
        return result.final_output

    def get_workflow_visualization(self) -> str:
        """Get a visual representation of the workflow."""
        try:
            return self.app.get_graph().draw_mermaid()
        except Exception as e:
            logger.error(f"Failed to generate workflow visualization: {e}")
            return "Workflow visualization not available"

