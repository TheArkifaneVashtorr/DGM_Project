# dgm_core/mutator.py
# This module contains the SelfMutator agent, responsible for self-modification.

import os
import shutil
import config.settings as settings
from dgm_core.llm_interface import LLMInterface

class SelfMutator:
    """
    An agent capable of proposing and packaging modifications to its own source code.
    """
    def __init__(self, llm_interface: LLMInterface, source_files: list):
        """
        Initializes the mutator.

        Args:
            llm_interface (LLMInterface): An initialized LLM interface.
            source_files (list): A list of source files the mutator is aware of.
        """
        self.llm = llm_interface
        self.source_files = source_files

    def propose_modification(self, target_file: str) -> str:
        """
        Uses the LLM to propose a modification to a target source file.

        Args:
            target_file (str): The path to the file to be modified.

        Returns:
            str: The complete, new source code for the target file, or an empty string on failure.
        """
        print(f"\n>>> Proposing modification for '{target_file}'...")
        try:
            with open(target_file, 'r') as f:
                original_code = f.read()
        except FileNotFoundError:
            print(f"Error: Target file '{target_file}' not found.")
            return ""

        # A more advanced system would generate this goal dynamically.
        improvement_goal = "Refactor the settings to use a dictionary for model configurations, which is more scalable. Add a new 'mutator_model' setting with the value 'mutator_model:latest' and rename 'solver_model' to 'solver_model:latest'."

        prompt = f"""
As a self-improving AI, your task is to rewrite the following source code file to achieve a specific goal.
Your output must be the complete, new version of the file. Do not add any extra text or explanations.

Goal: {improvement_goal}

Original file content of '{target_file}':
---
{original_code}
---

Provide the complete, rewritten file content now:
"""
        mutant_code = self.llm.query(prompt)
        return mutant_code

    def package_mutant(self, target_file: str, mutant_code: str) -> str:
        """
        Packages the proposed mutation into a new directory for testing.

        Args:
            target_file (str): The relative path of the file that was mutated.
            mutant_code (str): The new code for the target file.

        Returns:
            str: The path to the created mutant package directory.
        """
        mutant_package_dir = 'dgm_mutant_package'
        if os.path.exists(mutant_package_dir):
            shutil.rmtree(mutant_package_dir)
        os.makedirs(mutant_package_dir)

        # Copy all source files except the target file
        for src_path in self.source_files:
            if src_path != target_file:
                dest_path = os.path.join(mutant_package_dir, src_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy(src_path, dest_path)

        # Write the new mutant code to the target file path within the package
        mutant_file_path = os.path.join(mutant_package_dir, target_file)
        os.makedirs(os.path.dirname(mutant_file_path), exist_ok=True)
        with open(mutant_file_path, 'w') as f:
            f.write(mutant_code)

        # Copy benchmarks into the package for testing
        shutil.copytree('benchmarks', os.path.join(mutant_package_dir, 'benchmarks'))

        print(f"  Successfully packaged mutant into '{mutant_package_dir}'")
        return mutant_package_dir
