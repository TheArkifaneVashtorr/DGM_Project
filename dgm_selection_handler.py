# dgm_selection_handler.py
# Handles the selection process, persisting successful mutations.

import os
from dgm_core.dgm_genome import Genome

class SelectionHandler:
    """
    Applies the outcome of an evaluation, updating the master genome or environment.
    """
    def __init__(self, genome_filepath='dgm_genome.json', base_project_dir='.'):
        self.genome_filepath = genome_filepath
        self.base_project_dir = base_project_dir

    def select(self, parent_genome: Genome, mutant_genome: Genome, mutation_info: dict):
        """
        Compares fitness and persists the change if the mutant is superior.
        """
        print(f"\n[SELECTION HANDLER] Comparing mutant #{mutant_genome.genome_id} to parent #{parent_genome.genome_id}...")
        if mutant_genome.fitness > parent_genome.fitness:
            print(f"SUCCESS: Mutant fitness ({mutant_genome.fitness:.4f}) > Parent fitness ({parent_genome.fitness:.4f})")
            print("Adopting new configuration.")
            
            if mutation_info['type'] == 'ENVIRONMENT_MUTATION':
                self._apply_environment_mutation(mutation_info)
            
            mutant_genome.to_json(self.genome_filepath)
            print(f"Saved superior genome #{mutant_genome.genome_id} to {self.genome_filepath}")
        else:
            print(f"FAILURE: Mutant fitness ({mutant_genome.fitness:.4f}) <= Parent fitness ({parent_genome.fitness:.4f})")
            print("Discarding mutant. No changes made to base project.")

    def _apply_environment_mutation(self, mutation_info: dict):
        """
        Applies a successful environment mutation to the main project's requirements.txt
        and advises on rebuilding the Docker image.
        """
        print("[SELECTION HANDLER] Applying successful environment mutation to main project.")
        req_path = os.path.join(self.base_project_dir, 'requirements.txt')
        
        parts = mutation_info['details'].split("'")
        if len(parts) < 2: return
        library_to_add = parts[1]

        existing_reqs = []
        if os.path.exists(req_path):
            with open(req_path, 'r') as f:
                existing_reqs = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]

        if library_to_add not in existing_reqs:
            with open(req_path, 'a') as f:
                f.write(f"\n{library_to_add}")
            print(f"[SELECTION HANDLER] Added '{library_to_add}' to {req_path}.")
            
            print("\n--------------------- ACTION REQUIRED ---------------------")
            print("A new dependency has been added to requirements.txt.")
            print("The DGM Docker image must be rebuilt to include this dependency.")
            print("Execute the appropriate Docker build command for your system.")
            print("-----------------------------------------------------------\n")
