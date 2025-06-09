# config/settings.py
# Central configuration file for the Darwin Gödel Machine.

# --- Evolutionary Solver Settings ---
MAX_GENERATIONS = 10  # Max attempts for the solver to find a solution for a benchmark.
POPULATION_SIZE = 5   # Number of candidate solutions to generate per generation.
DIVERSITY_CLUSTER_COUNT = 3 # Number of top solution clusters to maintain for diversity.

# --- LLM Interface Settings ---
# Defines the names of the custom models to be built and used by Ollama.
SOLVER_MODEL_NAME = "solver_model:latest"
MUTATOR_MODEL_NAME = "mutator_model:latest"

# --- Knowledge Manager Settings ---
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "dgm_knowledge_base"

# --- Mutator Settings ---
MUTATION_TARGET_FILE = "config/settings.py" # A default, can be overridden.
