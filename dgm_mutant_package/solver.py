# solver.py
# Contains the EvolutionarySolver for solving a single programming task.

import config
from dgm_tools import evaluate_fitness

class EvolutionarySolver:
    def __init__(self, llm_interface, knowledge_manager):
        self.llm = llm_interface
        self.km = knowledge_manager

    def evolve(self, task_description, test_code, max_generations=10):
        """Evolves a solution for a given task, returns generations taken."""
        for gen in range(1, max_generations + 1):
            context = self.km.retrieve_context(task_description)
            prompt = config.RAG_PROMPT_TEMPLATE.format(context=context, task_description=task_description)
            
            generated_code = self.llm.generate(prompt)
            
            if evaluate_fitness(generated_code, test_code) == 1:
                print(f"Solved '{task_description}' in {gen} generation(s).")
                return gen
        
        print(f"Failed to solve '{task_description}' within {max_generations} generations.")
        return max_generations + 1
