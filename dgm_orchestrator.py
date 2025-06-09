# dgm_orchestrator.py
# The main orchestrator for the Darwin Gödel Machine's evolutionary cycles.

import os
import random
from dgm_core.dgm_genome import Genome
from dgm_core.self_mutator import SelfMutator
from dgm_core.evolutionary_solver import EvolutionarySolver
from dgm_mutant_manager import MutantManager
from dgm_selection_handler import SelectionHandler

class Orchestrator:
    """
    Manages the primary evolutionary loop of the DGM, including meta-evolution.
    """
    def __init__(self, genome_filepath='dgm_genome.json'):
        self.genome_filepath = genome_filepath
        self.ollama_base_url = "http://ollama:11434"
        self.parent_genome = self._load_genome()
        self.mutant_manager = MutantManager()
        self.selection_handler = SelectionHandler(genome_filepath)

    def _load_genome(self):
        """Loads the current parent genome or initializes a new one."""
        print("[ORCHESTRATOR] Loading Genome...")
        if os.path.exists(self.genome_filepath):
            genome = Genome.from_json(self.genome_filepath)
            print(f"Loaded genome #{genome.genome_id} (Gen: {genome.generation}, Fitness: {genome.fitness:.4f}) from {self.genome_filepath}.")
            return genome
        else:
            genome = Genome()
            genome.genome_id = 1
            print("No genome file found. Initializing with default genome #1.")
            genome.to_json(self.genome_filepath)
            return genome

    def run_evolutionary_cycle(self):
        """
        Executes one complete cycle of mutation, evaluation, and selection.
        """
        print(f"\n--- DGM ORCHESTRATOR: BEGINNING CYCLE FOR GENERATION {self.parent_genome.generation + 1} ---")
        
        mutator = SelfMutator(self.parent_genome, self.ollama_base_url)
        mutant_genome, mutation_info = mutator.propose_mutation()
        
        print("\n[EVALUATION] Evaluating mutant genome's performance...")
        mutant_fitness = self.mutant_manager.evaluate(mutant_genome, mutation_info)
        mutant_genome.fitness = mutant_fitness
        print(f"Mutant genome #{mutant_genome.genome_id} achieved fitness: {mutant_fitness:.4f}")

        self.selection_handler.select(self.parent_genome, mutant_genome, mutation_info)
        
        print("\n--- CYCLE COMPLETE ---")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run_evolutionary_cycle()
