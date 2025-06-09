# config/settings.py
# Central configuration file for the Darwin Gödel Machine.

# --- Evolutionary Solver Settings ---
MAX_GENERATIONS = 10  # Max attempts for the solver to find a solution for a benchmark.

# --- LLM Interface Settings ---
# Defines the names of the custom models to be built and used by Ollama.
# These names are used by the build process in run_dgm.py.
# The ":latest" tag is conventional.
SOLVER_MODEL_NAME = "solver_model:latest"
MUTATOR_MODEL_NAME = "mutator_model:latest"

# --- Knowledge Manager Settings ---
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "dgm_knowledge_base"

# --- Mutator Settings ---
MUTATION_TARGET_FILE = "config/settings.py" # A default, can be overridden.
