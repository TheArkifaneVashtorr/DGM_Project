# llm_interface.py
# Handles all API communication with the Ollama LLM service.

import requests
import random
import config
from dgm_tools import clean_code

class LLMInterface:
    def generate(self, prompt):
        """Sends a prompt to a randomly chosen model and gets a response."""
        llm_model = random.choice(config.AVAILABLE_MODELS)
        payload = {"model": llm_model, "prompt": prompt, "stream": False, "options": {"temperature": 0.25}}
        
        print(f"Sending prompt to LLM ({llm_model})...")
        try:
            response = requests.post(config.OLLAMA_API_URL, json=payload, timeout=180)
            response.raise_for_status()
            raw_response = response.json().get('response', '')
            return clean_code(raw_response)
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Ollama communication failed: {e}")
            return None
