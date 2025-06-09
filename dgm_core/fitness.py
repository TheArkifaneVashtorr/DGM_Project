# dgm_core/fitness.py
import time
import logging
from .verifier import Verifier
from config import settings

class Fitness:
    """
    Calculates the fitness of a code solution based on multiple objectives.
    """
    def __init__(self):
        self.verifier = Verifier()
        self.weights = settings.FITNESS_WEIGHTS
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        self.logger = logging.getLogger(__name__)

    def _calculate_correctness(self, execution_results, test_cases):
        """Calculates correctness score based on passing test cases."""
        passed_count = sum(1 for result, case in zip(execution_results, test_cases) if result == case['expected_output'])
        return passed_count / len(test_cases) if test_cases else 0

    def _calculate_efficiency(self, execution_time):
        """Calculates efficiency score. Lower time is better."""
        # Normalize time. This is a simple heuristic.
        # A 1-second execution gets a low score, near-zero gets a high score.
        return max(0, 1 - (execution_time / 2.0))

    def _calculate_simplicity(self, code):
        """Calculates simplicity score. Shorter code is simpler."""
        # Heuristic: Penalize long code. Assume a baseline of 20 lines is complex.
        lines = len(code.split('\n'))
        return max(0, 1 - (lines / 100.0))
        
    def calculate(self, code, execution_results, execution_time, test_cases):
        """
        Calculates the overall weighted fitness score for a solution.

        Returns:
            A tuple containing the weighted score and a dictionary of individual scores.
        """
        correctness_score = self._calculate_correctness(execution_results, test_cases)
        
        # If the code is not fully correct, other metrics are irrelevant.
        if correctness_score < 1.0:
            scores = {
                "correctness": correctness_score,
                "efficiency": 0,
                "simplicity": 0,
                "verifiability": 0
            }
            return 0.0, scores

        efficiency_score = self._calculate_efficiency(execution_time)
        simplicity_score = self._calculate_simplicity(code)
        
        verification_results = self.verifier.analyze(code)
        verifiability_score = verification_results.get("verifiability_score", 0.0)

        scores = {
            "correctness": correctness_score,
            "efficiency": efficiency_score,
            "simplicity": simplicity_score,
            "verifiability": verifiability_score
        }

        weighted_score = (
            scores["correctness"] * self.weights["correctness"] +
            scores["efficiency"] * self.weights["efficiency"] +
            scores["simplicity"] * self.weights["simplicity"] +
            scores["verifiability"] * self.weights["verifiability"]
        )

        return weighted_score, scores
