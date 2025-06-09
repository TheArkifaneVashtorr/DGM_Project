# dgm_core/llm_interface.py
# This module provides a streamlined interface for interacting with the Ollama service.

import ollama
import re

class LLMInterface:
    """A dedicated interface for all communications with the Ollama LLM service."""

    def __init__(self, model_name: str):
        """
        Initializes the interface with a specific model.

        Args:
            model_name (str): The name of the Ollama model to be used for interactions.
        """
        if not model_name:
            raise ValueError("A model name must be provided to LLMInterface.")
        self.model = model_name
        print(f"LLMInterface initialized for model: '{self.model}'")

    def _clean_response(self, response_text: str) -> str:
        """
        Cleans the LLM's response by removing code block markers and surrounding whitespace.

        Args:
            response_text (str): The raw response text from the LLM.

        Returns:
            str: The cleaned code, ready for execution or saving.
        """
        # Regex to find code within ```python ... ``` or ``` ... ```
        code_block_match = re.search(r"```(?:python\n)?(.*?)```", response_text, re.DOTALL)
        if code_block_match:
            return code_block_match.group(1).strip()
        # Fallback for responses that might not use markdown formatting
        return response_text.strip()

    def query(self, prompt: str) -> str:
        """
        Sends a prompt to the configured Ollama model and returns the cleaned response.

        Args:
            prompt (str): The input prompt for the LLM.

        Returns:
            str: The cleaned, ready-to-use response from the LLM.
        """
        print(f"\n--- Querying LLM ({self.model}) ---")
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            raw_text = response['message']['content']
            cleaned_code = self._clean_response(raw_text)
            print(f"--- LLM Response Received ---")
            return cleaned_code
        except Exception as e:
            print(f"Error communicating with Ollama model '{self.model}': {e}")
            # In a more robust system, this would include retry logic or fallbacks.
            return ""
