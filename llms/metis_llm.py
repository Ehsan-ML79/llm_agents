# import os
# import requests
# import logging
# from typing import Dict, Any, Optional

# logger = logging.getLogger(__name__)

# class LLMResponse:
#     """Simple response wrapper to provide .content attribute"""
#     def __init__(self, content: str):
#         self.content = content

# class MetisGeminiLLM:
#     """
#     Fixed implementation of MetisGeminiLLM that properly handles API responses
#     and returns consistent response objects with .content attribute
#     """
    
#     def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-flash"):
#         # Get API key from parameter or environment
#         self.api_key = api_key or os.getenv("METIS_API_KEY")
#         if not self.api_key:
#             raise ValueError("METIS_API_KEY must be provided either as parameter or environment variable")
        
#         self.model_name = model_name
#         self.base_url = "https://api.metis.ai/v1"  # Adjust this to actual Metis API endpoint
        
#         logger.info(f"Successfully initialized MetisGeminiLLM with model: {model_name}")
    
#     def invoke(self, prompt: str) -> LLMResponse:
#         """
#         Invoke the LLM with proper error handling and consistent response format
#         """
#         try:
#             # Prepare the API request
#             headers = {
#                 "Authorization": f"Bearer {self.api_key}",
#                 "Content-Type": "application/json"
#             }
            
#             payload = {
#                 "model": self.model_name,
#                 "prompt": prompt,
#                 "max_tokens": 2000,
#                 "temperature": 0.7
#             }
            
#             # Make the API call
#             response = requests.post(
#                 f"{self.base_url}/generate",  # Adjust endpoint as needed
#                 headers=headers,
#                 json=payload,
#                 timeout=30
#             )
            
#             response.raise_for_status()
            
#             # Parse the response
#             response_data = response.json()
            
#             # Extract content - adjust this based on actual Metis API response format
#             if isinstance(response_data, dict):
#                 # Try common response formats
#                 content = (response_data.get("content") or 
#                           response_data.get("text") or 
#                           response_data.get("response") or 
#                           response_data.get("output") or
#                           str(response_data))
#             else:
#                 content = str(response_data)
            
#             return LLMResponse(content)
            
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Error calling Metis Gemini API: {e}")
#             # Return a fallback response instead of crashing
#             return LLMResponse(f"API Error: {str(e)}")
#         except Exception as e:
#             logger.error(f"Error calling Metis Gemini API: {e}")
#             return LLMResponse(f"Unexpected error: {str(e)}")
import os
import logging
from typing import Optional
from openai import OpenAI  # pip install openai>=1.0.0

logger = logging.getLogger(__name__)

class LLMResponse:
    def __init__(self, content: str):
        self.content = content

class MetisGeminiLLM:
    def __init__(
        self,
        api_key: Optional[str]    = "tpsg-JwhFnuGQsuWfgM5q8xpOyCpmRWuI80n",
        model_name: str           = "gpt-4o",
        base_url: str             = "https://api.metisai.ir/openai/v1"
    ):
        # 1) Force the key if you passed it in, else grab from env
        self.api_key = api_key or os.getenv("METIS_API_KEY")
        if not self.api_key:
            raise ValueError("METIS_API_KEY must be set either as constructor arg or in environment")

        # 2) Mirror your repro: same args
        logger.info(f"▶️ Using METIS_API_KEY = {self.api_key!r}")
        logger.info(f"▶️ Talking to Metis at {base_url!r}, model alias {model_name!r}")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
        self.model_name = model_name

        logger.info(f"Initialized MetisGeminiLLM(client={self.client}, model={self.model_name!r})")

    def invoke(self, prompt: str) -> LLMResponse:
        try:
            # 3) Exactly what your repro does
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            # 4) Extract content
            content = response.choices[0].message.content
            return LLMResponse(content)

        except Exception as e:
            logger.error(f"Metis API call failed: {e}")
            # Echo back the full repr so we can see status codes, etc.
            return LLMResponse(f"Error: {e!r}")

