# dgm_core/self_mutator.py (With Few-Shot Prompting and Self-Correction)
# Proposes mutations to the DGM's genome and environment using a live LLM.

import requests
import json
import random
import copy
from dgm_core.dgm_genome import Genome

class SelfMutator:
    """
    Uses its designated mutator_model to propose modifications to a parent genome,
    with a self-correction mechanism.
    """
    def __init__(self, parent_genome: Genome, ollama_base_url: str = "http://ollama:11434"):
        self.parent_genome = parent_genome
        self.mutator_model = parent_genome.mutator_model
        self.ollama_base_url = ollama_base_url
        print(f"SelfMutator instantiated with LIVE cognitive engine: {self.mutator_model}")

    def _make_ollama_request(self, model: str, prompt: str):
        """Helper function to make requests to the Ollama API."""
        api_url = f"{self.ollama_base_url}/api/generate"
        payload = {"model": model, "prompt": prompt, "stream": False, "format": "json"}
        try:
            print(f"Sending request to Ollama for model '{model}'...")
            response = requests.post(api_url, json=payload, timeout=180)
            response.raise_for_status()
            response_json = json.loads(response.json()['response'])
            print("Ollama request successful.")
            return response_json
        except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError) as e:
            print(f"ERROR: Ollama request or parsing failed: {e}")
            return None

    def _get_initial_prompt(self) -> str:
        """Constructs the prompt to guide the LLM, now with a few-shot example."""
        genome_dict = copy.deepcopy(self.parent_genome.__dict__)
        return f"""
        You are an evolutionary AI research assistant. Your task is to propose a single, valid mutation to the provided DGM genome.
        Analyze the current genome and choose one of three mutation targets: 'solver_policy', 'mutator_model', or 'environment'.

        Current Genome:
        {json.dumps(genome_dict, indent=2)}

        Here is an example of a perfect response format:
        {{
          "target_gene": "solver_policy",
          "policy_key": "complexity_threshold",
          "new_value": 0.65,
          "reason": "The current threshold seems too high, experimenting with a lower value to favor the more efficient easy_model."
        }}

        Mutation Rules:
        1. If you choose 'mutator_model', set 'new_value' to one of these valid models: ['llama3:8b', 'codellama:13b', 'mistral:7b', 'gemma:7b'].
        2. If you choose 'solver_policy', you must also choose a 'policy_key' from ['easy_model', 'hard_model', 'complexity_threshold'].
            - For 'easy_model', 'new_value' must be one of: ['gemma:2b', 'tinydolphin', 'phi-2'].
            - For 'hard_model', 'new_value' must be one of: ['llama3:8b', 'codellama:13b', 'codellama:34b'].
            - For 'complexity_threshold', 'new_value' must be a float between 0.1 and 0.9.
        3. If you choose 'environment', set 'new_value' to a single, useful python library name to add, e.g., "numpy" or "pandas".
        4. Provide a brief 'reason' for your proposed mutation.

        Respond with a JSON object in the correct format and nothing else.
        """

    def _get_correction_prompt(self, failed_response: str, error: str) -> str:
        # ... [This method remains the same] ...
        return f"""
        Your previous attempt to generate a mutation JSON was invalid.
        
        Previous invalid response:
        {failed_response}

        The error encountered when parsing was:
        {error}

        Please analyze the error and your previous response. Generate a new, corrected JSON object that strictly follows all the rules from the original prompt. Pay close attention to the required fields and valid values for each 'target_gene'. For 'solver_policy', you MUST include a 'policy_key'.
        
        Provide only the corrected JSON object.
        """

    def propose_mutation(self) -> (Genome, dict):
        # ... [This method remains the same] ...
        print("Proposing mutation via LLM...")
        
        max_attempts = 2
        last_failed_response = None
        last_error = "Initial attempt failed."

        for attempt in range(max_attempts):
            if attempt == 0:
                prompt = self._get_initial_prompt()
            else:
                print(f"Self-Correction Attempt {attempt}...")
                prompt = self._get_correction_prompt(str(last_failed_response), str(last_error))

            mutation_proposal = self._make_ollama_request(self.mutator_model, prompt)
            last_failed_response = mutation_proposal

            if not mutation_proposal:
                last_error = "LLM response was None."
                continue

            try:
                mutant_genome = copy.deepcopy(self.parent_genome)
                mutation_info = self._apply_mutation(mutant_genome, mutation_proposal)
                return mutant_genome, mutation_info
            except Exception as e:
                last_error = e
                print(f"Error applying LLM-proposed mutation (Attempt {attempt + 1}/{max_attempts}): {e}")
        
        print("LLM self-correction failed after multiple attempts. Falling back to random mutation.")
        return self._fallback_random_mutation()


    def _apply_mutation(self, genome: Genome, proposal: dict) -> dict:
        # ... [This method remains the same] ...
        target = proposal.get("target_gene")
        new_value = proposal.get("new_value")
        reason = proposal.get("reason", "No reason provided.")
        
        print(f"LLM proposed mutation: Target='{target}', NewValue='{new_value}'. Reason: {reason}")
        
        mutation_info = {'type': 'GENOMIC_MUTATION', 'details': ''}
        
        if target == "solver_policy":
            policy_key = proposal.get("policy_key")
            if policy_key not in genome.solver_policy:
                raise ValueError(f"Invalid or missing 'policy_key' for solver_policy mutation.")
            genome.solver_policy[policy_key] = new_value
            mutation_info['details'] = f"Changed solver_policy.{policy_key} to {new_value}"
        elif target == "mutator_model":
            genome.mutator_model = new_value
            mutation_info['details'] = f"Changed mutator_model to {new_value}"
        elif target == "environment":
            mutation_info['type'] = 'ENVIRONMENT_MUTATION'
            mutation_info['details'] = f"Add the '{new_value}' library to requirements.txt"
        else:
            raise ValueError(f"Invalid mutation target: {target}")

        genome.parent_id = self.parent_genome.genome_id
        genome.generation = self.parent_genome.generation + 1
        genome.genome_id = self.parent_genome.genome_id + 1
        genome.fitness = 0.0
        return mutation_info

    def _fallback_random_mutation(self) -> (Genome, dict):
        # ... [This method remains the same] ...
        mutant_genome = copy.deepcopy(self.parent_genome)
        mutant_genome.parent_id = self.parent_genome.genome_id
        mutant_genome.generation = self.parent_genome.generation + 1
        mutant_genome.genome_id = self.parent_genome.genome_id + 1
        mutant_genome.fitness = 0.0
        
        change = random.uniform(-0.1, 0.1)
        new_threshold = mutant_genome.solver_policy['complexity_threshold'] + change
        mutant_genome.solver_policy['complexity_threshold'] = max(0.1, min(0.9, round(new_threshold, 4)))
        details = f"Fallback Random: Changed threshold to {mutant_genome.solver_policy['complexity_threshold']}"
        print(details)
        return mutant_genome, {'type': 'GENOMIC_MUTATION', 'details': details}
