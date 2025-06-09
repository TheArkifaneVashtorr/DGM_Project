---
# config/settings.py
# Central configuration file for the Darwin Gödel Machine.

# --- Evolutionary Solver Settings ---
MAX_GENERATIONS = 10  # Max attempts for the solver to find a solution for a benchmark.
POPULATION_SIZE = 5   # Number of candidate solutions to generate per generation.
DIVERSITY_CLUSTER_COUNT = 3 # Number of top solution clusters to maintain for diversity.

MODEL_CONFIGS = {
    "solver_model": "solver_model:latest",
    "mutator_model": "mutator_model:latest"
}

# --- Knowledge Manager Settings ---
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "dgm_knowledge_base"

# --- Mutator Settings ---
MUTATION_TARGET_FILE = "config/settings.py" # A default, can be overridden.
---