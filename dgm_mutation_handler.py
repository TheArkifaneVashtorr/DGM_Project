# dgm_mutation_handler.py
import os
import copy
import logging

from dgm_core.self_mutator import SelfMutator
from dgm_core.dgm_genome import DGMGenome
from dgm_mutant_manager import MutantManager
from config import settings

class MutationHandler:
    """Handles the full lifecycle of proposing and evaluating a mutation."""

    def __init__(self, mutator: SelfMutator, mutant_manager: MutantManager):
        self.mutator = mutator
        self.mutant_manager = mutant_manager
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        self.logger = logging.getLogger(__name__)

    def perform_mutation_cycle(self, parent_genome: DGMGenome, parent_score: float, is_stagnant: bool) -> tuple[float, DGMGenome | dict | None]:
        """
        Generates a goal, creates a mutant, evaluates it, and returns the result.

        Returns:
            A tuple containing:
            - mutant_score (float): The performance score of the mutant.
            - proposed_change (DGMGenome | dict | None): The proposed change.
              - DGMGenome if it was a genomic mutation.
              - dict with {'path': str, 'code': str} if file mutation.
              - None if mutation failed.
        """
        self.logger.info(f"\n\n=== [PHASE 2] Generating Strategic Goal for Self-Modification ===")
        goal = self.mutator.generate_strategic_goal(parent_genome, is_stagnant)
        self.logger.info(f"Generated Strategic Goal: {goal}")

        if goal.startswith("GENOMIC_MUTATION:"):
            try:
                # Parse goal like "GENOMIC_MUTATION: Set solver_model to 'llama3:8b'"
                gene_name, new_value_str = goal.split("Set")[1].strip().split(" to ")
                gene_name = gene_name.strip()
                new_value = new_value_str.strip().strip("'")

                mutant_genome = copy.deepcopy(parent_genome)
                mutant_genome.set_gene(gene_name, new_value)
                
                return "GENOMIC", mutant_genome

            except Exception as e:
                self.logger.error(f"Failed to parse genomic mutation goal: '{goal}'. Error: {e}")
                return "FAILED", None

        elif goal.startswith("FILE_MUTATION:"):
            if parent_score == float('inf'):
                self.logger.warning("Skipping file mutation because parent failed evaluation.")
                return "SKIPPED", None

            file_goal = goal.split(":", 1)[1].strip()
            target_file_abs_path = settings.MUTATION_TARGET_FILE
            
            proposed_code = self.mutator.propose_modification(target_file_abs_path, file_goal)

            if not proposed_code:
                self.logger.warning(">>> MUTATION FAILED: Could not generate valid code. <<<")
                return "FAILED", None

            change_details = {
                "path": target_file_abs_path,
                "code": proposed_code
            }
            return "FILE", change_details
        
        else:
            self.logger.warning(f"Unknown goal type generated: {goal}")
            return "FAILED", None
