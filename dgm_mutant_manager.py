# dgm_mutant_manager.py
# Manages the setup and evaluation of DGM mutants.

import os
import shutil
import subprocess
import random
from dgm_core.dgm_genome import Genome

class MutantManager:
    """
    Handles the creation of temporary environments for mutants and runs their evaluation.
    """
    def __init__(self, base_project_dir='.'):
        self.base_project_dir = base_project_dir
        self.temp_mutant_dir = os.path.join(self.base_project_dir, 'mutant_workspace')

    def evaluate(self, mutant_genome: Genome, mutation_info: dict) -> float:
        """
        Evaluates a mutant genome, creating a special environment if necessary.
        """
        print(f"\n[MUTANT MANAGER] Evaluating mutant #{mutant_genome.genome_id}...")
        print(f"[MUTANT MANAGER] Mutation Type: {mutation_info['type']}")

        if mutation_info['type'] == 'ENVIRONMENT_MUTATION':
            return self._evaluate_in_temp_env(mutant_genome, mutation_info)
        else: # GENOMIC_MUTATION
            return self._evaluate_in_place(mutant_genome)

    def _evaluate_in_place(self, genome: Genome) -> float:
        """Simulates evaluation for a simple genomic mutation."""
        print("[MUTANT MANAGER] Evaluating genome change in current environment.")
        return round(random.uniform(0.1, 1.0), 4)

    def _evaluate_in_temp_env(self, genome: Genome, mutation_info: dict) -> float:
        """
        Creates a temporary environment, applies environment mutation, and evaluates.
        """
        if os.path.exists(self.temp_mutant_dir):
            shutil.rmtree(self.temp_mutant_dir)
        os.makedirs(self.temp_mutant_dir)
        print(f"[MUTANT MANAGER] Created temporary directory: {self.temp_mutant_dir}")

        try:
            # 1. Handle requirements.txt modification
            print(f"[MUTANT MANAGER] Applying environment mutation: {mutation_info['details']}")
            self._create_mutant_requirements(mutation_info)

            # 2. Simulate installing dependencies in a virtual environment
            print("[MUTANT MANAGER] Simulating pip install in mutant's virtual environment...")
            print("SIMULATION: Dependencies installed successfully.")
            
            # 3. Simulate running a benchmark in the new environment
            print("[MUTANT MANAGER] Simulating benchmark execution in new environment...")
            fitness = round(random.uniform(0.5, 1.0), 4) # Higher potential fitness for new tools
            
        except Exception as e:
            print(f"[MUTANT MANAGER] Evaluation failed in temporary environment: {e}")
            fitness = 0.0 # Failed evaluation
        finally:
            # 4. Clean up the temporary directory
            print(f"[MUTANT MANAGER] Cleaning up temporary directory: {self.temp_mutant_dir}")
            shutil.rmtree(self.temp_mutant_dir)
            
        return fitness

    def _create_mutant_requirements(self, mutation_info: dict):
        """Creates the new requirements.txt for the mutant."""
        base_req_path = os.path.join(self.base_project_dir, 'requirements.txt')
        mutant_req_path = os.path.join(self.temp_mutant_dir, 'requirements.txt')
        
        parts = mutation_info['details'].split("'")
        if len(parts) < 2:
            raise ValueError("Invalid environment mutation detail format.")
        library_to_add = parts[1]

        existing_reqs = []
        if os.path.exists(base_req_path):
            with open(base_req_path, 'r') as f:
                existing_reqs = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
        
        if library_to_add not in existing_reqs:
            existing_reqs.append(library_to_add)
        
        with open(mutant_req_path, 'w') as f:
            f.write("# DGM Mutant Dependencies\n")
            for req in existing_reqs:
                f.write(f"{req}\n")
        print(f"[MUTANT MANAGER] Created mutant requirements.txt at {mutant_req_path}")
