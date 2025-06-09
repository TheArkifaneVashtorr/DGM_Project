---
# config/settings.py
# Central configuration file for the Darwin Gödel Machine.

# --- Evolutionary Solver Settings ---
MAX_GENERATIONS = 10  # Max attempts for the solver to find a solution for a benchmark.
POPULATION_SIZE = 5   # Number of candidate solutions to generate per generation.

MODEL_CONFIGS = {
    'mutator_model': 'mutator_model:latest',
    'solver_model': 'solver_model:latest'
}

# --- LLM Interface Settings ---
# Defines the names of the custom models to be built and used by Ollama.
# These names are used by the build process in run_dgm.py.
# The ":latest" tag is conventional.

# --- Knowledge Manager Settings ---
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "dgm_knowledge_base"

# --- Mutator Settings ---
MUTATION_TARGET_FILE = "config/settings.py" # A default, can be overridden.