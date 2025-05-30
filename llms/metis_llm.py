# hunter/llms/metis_llm.py

from typing import Any, List, Optional
import google.generativeai as genai
from google.api_core.client_options import ClientOptions
from langchain_core.language_models import LLM
from langchain_core.outputs import Generation, LLMResult
from pydantic import Field
import logging

# Set up logging to help with debugging
logger = logging.getLogger(__name__)

class MetisGeminiLLM(LLM):
    """
    Custom LLM wrapper for MetisAI's Gemini API integration.
    
    This class provides a LangChain-compatible interface for the Metis.ai
    Gemini service, handling API configuration, response processing, and
    error management for reliable operation in your agent pipeline.
    
    The key challenge here is that Pydantic (which LangChain uses for validation)
    doesn't know how to handle Google's GenerativeModel objects. We solve this
    by excluding the model field from validation and initializing it manually.
    """
    
    # These fields will be validated by Pydantic
    api_key: str = Field(description="API key for Metis.ai service")
    model_name: str = Field(default="gemini-1.5-flash", description="Name of the Gemini model to use")
    endpoint: str = Field(default="https://api.metisai.ir", description="Metis.ai API endpoint")
    
    # This field is excluded from Pydantic validation entirely
    # We'll set it manually in __init__ after the parent class is initialized
    model: Any = Field(default=None, exclude=True)
    
    class Config:
        """Pydantic configuration for this model"""
        # Allow arbitrary types (needed for Google AI objects)
        arbitrary_types_allowed = True
        # Don't validate assignment to excluded fields
        validate_assignment = False

    def __init__(self, **kwargs):
        """
        Initialize the MetisGeminiLLM with proper API configuration.
        
        This initialization process is crucial because we need to:
        1. Let Pydantic handle the basic field validation first
        2. Configure the Google AI client with our custom endpoint
        3. Create the GenerativeModel instance after everything else is set up
        
        This order prevents Pydantic from trying to validate the Google AI objects.
        """
        # First, initialize the parent LLM class with Pydantic validation
        super().__init__(**kwargs)
        
        try:
            # Configure the Google Generative AI client to use Metis endpoint
            # This is where we redirect Google's client to use Metis.ai instead
            genai.configure(
                api_key=self.api_key,
                transport='rest',  # Use REST transport for compatibility
                client_options=ClientOptions(api_endpoint=self.endpoint)
            )
            
            # Create the generative model instance
            # We do this after Pydantic initialization to avoid validation issues
            self.model = genai.GenerativeModel(self.model_name)
            
            logger.info(f"Successfully initialized MetisGeminiLLM with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize MetisGeminiLLM: {e}")
            # Set model to None so we can handle this gracefully later
            self.model = None
            raise RuntimeError(f"Could not initialize Metis Gemini client: {e}")

    @property
    def _llm_type(self) -> str:
        """Return the type identifier for this LLM implementation"""
        return "metis_gemini"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        Internal method to make API calls to the Metis Gemini service.
        
        This method handles the actual communication with the API and includes
        error handling to make your system more robust during demonstrations.
        
        Args:
            prompt: The text prompt to send to the model
            stop: Optional stop sequences (not supported by current Metis API)
            
        Returns:
            Generated text response as a string
            
        Note: The stop parameter is ignored because the current Metis API
        doesn't support stop sequences directly. In a production system,
        you might implement stop sequence handling in post-processing.
        """
        
        if not self.model:
            raise RuntimeError("Model not initialized - check API key and connection")
        
        try:
            # Make the API call to generate content
            logger.debug(f"Sending prompt to Metis Gemini: {prompt[:100]}...")
            response = self.model.generate_content(prompt)
            
            # Extract text from response
            if hasattr(response, 'text') and response.text:
                logger.debug("Successfully received response from Metis Gemini")
                return response.text
            else:
                # Handle edge cases where response might not have text
                logger.warning("Received response without text content")
                return "No response generated"
                
        except Exception as e:
            logger.error(f"Error calling Metis Gemini API: {e}")
            # Return a meaningful error message rather than crashing
            return f"Error generating response: {str(e)}"

    def generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        callbacks: Optional[Any] = None,
        **kwargs
    ) -> LLMResult:
        """
        Generate responses for multiple prompts in batch.
        
        This method implements the LangChain interface for batch processing,
        which is useful when you need to process multiple prompts efficiently.
        
        Args:
            prompts: List of text prompts to process
            stop: Optional stop sequences (passed through but not used)
            callbacks: LangChain callbacks for monitoring (not implemented)
            **kwargs: Additional arguments (ignored for now)
            
        Returns:
            LLMResult containing all generated responses
        """
        
        generations = []
        
        # Process each prompt individually
        # In a production system, you might want to implement true batch processing
        # if the API supports it, which can be more efficient
        for prompt in prompts:
            try:
                response_text = self._call(prompt, stop=stop)
                generations.append(Generation(text=response_text))
            except Exception as e:
                logger.error(f"Failed to generate response for prompt: {e}")
                # Include error information in the generation rather than failing completely
                generations.append(Generation(text=f"Generation failed: {str(e)}"))
        
        # Return all generations as a single result
        # LangChain expects generations to be nested in a list, even for single batches
        return LLMResult(generations=[generations])
    
    def invoke(self, prompt: str) -> 'LLMResponse':
        """
        High-level method to invoke the LLM and return a structured response.
        
        This method provides a simple interface that your agents can use
        without worrying about the underlying LangChain complexity.
        
        Returns an object with a .content attribute for consistency with
        your existing agent code.
        """
        response_text = self._call(prompt)
        return LLMResponse(content=response_text)
    
    def test_connection(self) -> bool:
        """
        Test the API connection with a simple prompt.
        
        This is useful for debugging and ensuring your API key is working
        before you start your main processing pipeline.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_response = self.invoke("Hello, please respond with 'Connection successful'")
            return "successful" in test_response.content.lower()
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

class LLMResponse:
    """
    Simple response wrapper to provide consistent interface.
    
    This class ensures that your agent code can always access response.content
    regardless of the underlying LLM implementation details.
    """
    
    def __init__(self, content: str):
        self.content = content
    
    def __str__(self):
        return self.content
    
    def __repr__(self):
        return f"LLMResponse(content='{self.content[:50]}...')"