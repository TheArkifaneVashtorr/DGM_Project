# dgm_core/llm_interface.py
import ollama
import logging
from config import settings

class LLMInterface:
    """
    A standardized interface for interacting with different LLMs via Ollama,
    now correctly configured for a Docker Compose environment.
    """
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = None
        self.model_params = {
            "temperature": 0.5,
            "top_k": 40,
            "top_p": 0.9,
        }
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        self.logger = logging.getLogger(__name__)

    def initialize_model(self):
        """Initializes the Ollama client with the correct host."""
        try:
            self.client = ollama.Client(host=settings.OLLAMA_HOST_URL)
            self.client.list()
            self.logger.info(f"LLMInterface initialized for model: '{self.model_name}'")
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama client for model {self.model_name}. Is Ollama running at {settings.OLLAMA_HOST_URL}? Error: {e}")
            self.client = None

    def set_model_params(self, **params):
        """Sets parameters for the next LLM query."""
        self.model_params.update(params)

    def query(self, prompt: str) -> str:
        """Sends a prompt to the LLM and returns the response."""
        if not self.client:
            self.logger.error("LLM client not initialized. Cannot send query.")
            return "Error: LLM client is not available."
            
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options=self.model_params
            )
            return response['message']['content']
        except Exception as e:
            self.logger.error(f"An error occurred while querying model {self.model_name}: {e}")
            return f"Error: Failed to get response from model {self.model_name}."
