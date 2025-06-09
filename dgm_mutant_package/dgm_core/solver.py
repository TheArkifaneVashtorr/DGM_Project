# dgm_core/solver.py
# This module contains the EvolutionarySolver agent responsible for solving programming tasks.

import config.settings as settings
from utils.tools import evaluate_fitness
from dgm_core.llm_interface import LLMInterface
from dgm_core.knowledge_manager import KnowledgeManager

class EvolutionarySolver:
    """
    An agent that uses a population-based evolutionary loop to solve programming tasks,
    inspired by principles from AlphaCode and evolutionary computation.
    """
    def __init__(self, llm_interface: LLMInterface, knowledge_manager: KnowledgeManager):
        """
        Initializes the solver.

        Args:
            llm_interface (LLMInterface): An initialized LLM interface for generation.
            knowledge_manager (KnowledgeManager): The system's knowledge manager for context.
        """
        self.llm = llm_interface
        self.km = knowledge_manager

    def evolve(self, task_description: str, test_code: str, max_generations: int = settings.MAX_GENERATIONS) -> int:
        """
        Attempts to solve a programming task through a population-based evolutionary loop.

        Args:
            task_description (str): The natural language description of the task.
            test_code (str): The Python code used to test the solution's fitness.
            max_generations (int): The maximum number of attempts (generations).

        Returns:
            int: The number of generations it took to find a solution, or max_generations if it failed.
        """
        print(f"\n>>> Solving Task: {task_description[:80]}...")
        
        # A simple mechanism to carry forward the "genetic material" of the best attempt
        best_solution_from_last_gen = "No previous solution." 

        for gen in range(1, max_generations + 1):
            print(f"  Generation {gen}/{max_generations}")

            population = []
            for i in range(settings.POPULATION_SIZE):
                print(f"    - Generating candidate {i+1}/{settings.POPULATION_SIZE}")
                context = self.km.retrieve_context(f"Context for solving this task: {task_description}")
                
                # The prompt now includes the best-performing code from the previous generation
                prompt = f"""
Based on the following context and the best-performing (but still incorrect) solution from the last attempt, please solve the programming task.
Task: {task_description}

Context from existing system knowledge:
---
{context}
---

Best solution from the last attempt:
---
{best_solution_from_last_gen}
---

Provide only the complete, executable Python code for the new solution. Your code should be an improvement.
"""
                solution_code = self.llm.query(prompt)
                if solution_code:
                    population.append(solution_code)

            if not population:
                print("  LLM failed to generate any candidates this generation. Continuing.")
                continue

            fittest_candidate = None
            highest_fitness = -1.0

            for i, candidate_code in enumerate(population):
                fitness = evaluate_fitness(candidate_code, test_code)
                print(f"    - Candidate {i+1} Fitness: {fitness}")
                if fitness == 1.0:
                    print(f"  Task solved successfully in {gen} generation(s).")
                    return gen
                if fitness > highest_fitness:
                    highest_fitness = fitness
                    fittest_candidate = candidate_code
            
            # Carry over the best solution for the next prompt
            best_solution_from_last_gen = fittest_candidate if fittest_candidate else "No solution was viable."
            print(f"  Highest fitness this generation: {highest_fitness}. Evolving...")

        print(f"  Failed to solve task within {max_generations} generations.")
        return max_generations
