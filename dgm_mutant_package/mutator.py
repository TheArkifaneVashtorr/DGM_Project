# mutator.py
# Manages the self-modification (mutation) process.

import os
import shutil
import config

class SelfMutator:
    def __init__(self, llm_interface, source_files):
        self.llm = llm_interface
        self.source_files = source_files

    def propose_modification(self, target_file):
        """Proposes a modification to a target source file."""
        print(f"Attempting to evolve the RAG prompt in '{target_file}'...")
        with open(target_file, 'r') as f:
            source_code = f.read()
        
        prompt = config.SELF_MODIFY_PROMPT_TEMPLATE.format(source_code=source_code)
        
        mutant_code = self.llm.generate(prompt)
        
        if not mutant_code or "RAG_PROMPT_TEMPLATE" not in mutant_code:
            print(f"ERROR: LLM did not return a valid config file. Response:\n{mutant_code[:500]}...")
            return None
        
        return mutant_code

    def package_mutant(self, target_file, mutant_code):
        """Creates a runnable package for the mutant."""
        package_dir = "dgm_mutant_package"
        if os.path.exists(package_dir): shutil.rmtree(package_dir)
        os.makedirs(package_dir)

        # Copy all original source files into the new package directory
        for f in self.source_files:
            # Do not copy the file that is being replaced by the mutant
            if os.path.basename(f) != os.path.basename(target_file):
                shutil.copy(f, package_dir)
        
        # Write the mutant code to the target file name inside the package
        with open(os.path.join(package_dir, os.path.basename(target_file)), "w") as f:
            f.write(mutant_code)
        
        # Copy other necessary files for the benchmark run
        shutil.copy("benchmark_suite.json", package_dir)
        if os.path.exists(config.KNOWLEDGE_BASE_DIR):
            shutil.copytree(config.KNOWLEDGE_BASE_DIR, os.path.join(package_dir, config.KNOWLEDGE_BASE_DIR))
            
        print(f"Mutant package created at '{package_dir}'.")
        return package_dir
