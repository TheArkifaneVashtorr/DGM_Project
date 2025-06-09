# dgm_core/evolutionary_solver.py
# The component responsible for solving tasks based on the current genome by calling a live Ollama service.

import requests
import json
from dgm_core.dgm_genome import Genome

class EvolutionarySolver:
    """
    Dynamically selects a live LLM via Ollama based on task complexity and the genome's policy.
    """
    def __init__(self, genome: Genome, ollama_base_url: str = "http://ollama:11434"):
        self.genome = genome
        self.ollama_base_url = ollama_base_url
        self.easy_model_name = self.genome.solver_policy.get('easy_model', 'gemma:2b')
        self.hard_model_name = self.genome.solver_policy.get('hard_model', 'llama3:8b')
        self.complexity_threshold = self.genome.solver_policy.get('complexity_threshold', 0.7)
        print(f"Solver initialized with LIVE policy: Easy='{self.easy_model_name}', Hard='{self.hard_model_name}', Threshold='{self.complexity_threshold}'")

    def _make_ollama_request(self, model: str, prompt: str, stream: bool = False):
        """Helper function to make requests to the Ollama API."""
        api_url = f"{self.ollama_base_url}/api/generate"
        payload = {"model": model, "prompt": prompt, "stream": stream}
        try:
            print(f"Sending request to Ollama for model '{model}'...")
            response = requests.post(api_url, json=payload, timeout=300) # 5-minute timeout
            response.raise_for_status()
            print("Ollama request successful.")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Ollama API request failed for model '{model}': {e}")
            return None

    def _analyze_task_complexity(self, task_description: str) -> float:
        """
        Uses the 'easy_model' to perform a heuristic analysis of the task's complexity.
        """
        print(f"Analyzing task complexity using model: {self.easy_model_name}...")
        prompt = f"""
        Analyze the following software development task and rate its complexity on a scale from 0.0 (trivial) to 1.0 (extremely complex). 
        Provide only a single floating-point number in your response and nothing else.
        TASK: "{task_description}"
        COMPLEXITY:
        """
        response_data = self._make_ollama_request(self.easy_model_name, prompt)
        
        if response_data and 'response' in response_data:
            try:
                complexity = float(response_data['response'].strip())
                complexity = max(0.0, min(1.0, complexity)) # Clamp value
                print(f"Analyzed task complexity: {complexity:.2f}")
                return complexity
            except (ValueError, TypeError):
                print(f"Warning: Could not parse complexity score from model response: '{response_data['response']}'. Defaulting to 0.5.")
                return 0.5
        
        print("Warning: Complexity analysis failed. Defaulting to 0.5.")
        return 0.5

    def solve(self, task_description: str) -> str:
        """
        Solves a task using the policy-selected live LLM.
        """
        task_complexity = self._analyze_task_complexity(task_description)

        if task_complexity < self.complexity_threshold:
            selected_model_name = self.easy_model_name
            print(f"Complexity ({task_complexity:.2f}) is below threshold ({self.complexity_threshold}). Using easy model: {selected_model_name}")
        else:
            selected_model_name = self.hard_model_name
            print(f"Complexity ({task_complexity:.2f}) is above or equal to threshold ({self.complexity_threshold}). Using hard model: {selected_model_name}")

        print(f"Solving task with live model {selected_model_name}...")
        prompt = f"Provide a complete code solution for the following task:\n\n{task_description}"
        response_data = self._make_ollama_request(selected_model_name, prompt)

        if response_data and 'response' in response_data:
            return response_data['response']
        
        return f"// Failed to get solution from model {selected_model_name}"
