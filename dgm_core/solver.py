# dgm_core/solver.py
# This module contains the EvolutionarySolver agent responsible for solving programming tasks.

import config.settings as settings
from utils.tools import evaluate_fitness
from dgm_core.llm_interface import LLMInterface
from dgm_core.knowledge_manager import KnowledgeManager

class EvolutionarySolver:
    """
    An agent that uses an evolutionary loop to solve programming tasks.
    """
    def __init__(self, llm_interface: LLMInterface, knowledge_manager: KnowledgeManager):
        """
        Initializes the solver.

        Args:
            llm_interface (LLMInterface): An initialized LLM interface to use for generation.
            knowledge_manager (KnowledgeManager): The system's knowledge manager for context.
        """
        self.llm = llm_interface
        self.km = knowledge_manager

    def evolve(self, task_description: str, test_code: str, max_generations: int = settings.MAX_GENERATIONS) -> int:
        """
        Attempts to solve a programming task through an evolutionary loop.

        Args:
            task_description (str): The natural language description of the task.
            test_code (str): The Python code used to test the solution's fitness.
            max_generations (int): The maximum number of attempts (generations).

        Returns:
            int: The number of generations it took to find a solution, or max_generations if it failed.
        """
        print(f"\n>>> Solving Task: {task_description[:80]}...")
        for gen in range(1, max_generations + 1):
            print(f"  Generation {gen}/{max_generations}")

            context = self.km.retrieve_context(f"Context for solving this task: {task_description}")
            prompt = f"""
Based on the following context, please solve the programming task.
Task: {task_description}
Context from existing system knowledge:
---
{context}
---
Provide only the complete, executable Python code for the solution.
"""
            solution_code = self.llm.query(prompt)

            if not solution_code:
                print("  LLM failed to generate a solution. Continuing to next generation.")
                continue

            fitness = evaluate_fitness(solution_code, test_code)

            if fitness == 1.0:
                print(f"  Task solved successfully in {gen} generation(s).")
                return gen

            print(f"  Solution failed fitness test (Fitness: {fitness}).")

        print(f"  Failed to solve task within {max_generations} generations.")
        return max_generations
