# dgm_core/dgm_config.py
from config import settings

class DGMConfig:
    """
    Provides a structured interface for accessing configuration settings.
    This class loads values from the central settings.py file.
    """
    def __init__(self):
        self._config = {
            # --- Model Configuration ---
            "available_solver_models": settings.AVAILABLE_SOLVER_MODELS,
            "default_solver_model": settings.DEFAULT_SOLVER_MODEL,
            "mutator_model": settings.MUTATOR_MODEL,
            
            # --- Evolutionary Solver Settings ---
            "max_generations": settings.MAX_GENERATIONS,
            "population_size": settings.POPULATION_SIZE,
            "elitism_count": settings.ELITISM_COUNT,
            "tournament_size": settings.TOURNAMENT_SIZE,

            # --- Fitness Evaluation Settings ---
            "fitness_weights": settings.FITNESS_WEIGHTS
        }

    def get(self, key: str):
        """
        Retrieves a configuration value by its key.
        """
        return self._config.get(key)
