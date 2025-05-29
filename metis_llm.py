# metis_llm.py
from langchain_core.language_models import LLM
from langchain_core.outputs import Generation, LLMResult
from typing import List, Optional
import google.generativeai as genai
from google.api_core.client_options import ClientOptions


class MetisGeminiLLM(LLM):
    model_name: str = "gemini-1.5-flash"
    api_key: str = ""
    endpoint: str = "https://api.metisai.ir"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        genai.configure(
            api_key=self.api_key,
            transport="rest",
            client_options=ClientOptions(api_endpoint=self.endpoint)
        )
        self.model = genai.GenerativeModel(self.model_name)

    @property
    def _llm_type(self) -> str:
        return "metis_gemini"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    def generate(self, prompts: List[str]) -> LLMResult:
        generations = [Generation(text=self._call(prompt)) for prompt in prompts]
        return LLMResult(generations=[generations])
