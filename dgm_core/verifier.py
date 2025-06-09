# dgm_core/verifier.py
import ast
import logging

class Verifier:
    """
    Analyzes code for formal properties and potential logical errors.
    In DGM v9.0, this is upgraded to perform Abstract Syntax Tree (AST) analysis.
    """

    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        self.logger = logging.getLogger(__name__)

    def _check_for_potential_index_errors(self, tree: ast.AST) -> float:
        """
        Heuristically checks for potential IndexError by analyzing loops and subscripts.
        This is a simple verifier; more advanced analysis is possible.
        
        Returns a score from 0.0 (high risk) to 1.0 (low risk).
        A very basic check: if a loop over range(len(x)) uses x[i+1], flag it.
        """
        score = 1.0
        for node in ast.walk(tree):
            # Check for loops like 'for i in range(len(some_list))'
            if isinstance(node, ast.For) and isinstance(node.iter, ast.Call):
                call = node.iter
                if isinstance(call.func, ast.Name) and call.func.id == 'range':
                    if call.args and isinstance(call.args[0], ast.Call):
                        len_call = call.args[0]
                        if isinstance(len_call.func, ast.Name) and len_call.func.id == 'len':
                            # We have a 'for i in range(len(list_name))' loop
                            # Now, look for risky subscripts inside this loop
                            for sub_node in ast.walk(node):
                                if isinstance(sub_node, ast.Subscript):
                                    # Check if the subscript index is 'i + constant'
                                    if (isinstance(sub_node.slice, ast.BinOp) and
                                        isinstance(sub_node.slice.op, ast.Add) and
                                        isinstance(sub_node.slice.left, ast.Name) and
                                        sub_node.slice.left.id == node.target.id):
                                        self.logger.warning("Verifier Warning: Potential IndexError due to index offset in loop.")
                                        score = 0.5 # Penalize potential off-by-one error
                                        break # Found one issue, no need to check further in this loop
            if score < 1.0:
                break
        return score


    def analyze(self, code: str) -> dict[str, float]:
        """
        Performs static analysis on the given code.
        
        Args:
            code (str): The source code to analyze.

        Returns:
            dict: A dictionary of verification scores.
                  For now, contains 'verifiability_score'.
        """
        results = {"verifiability_score": 1.0}

        try:
            tree = ast.parse(code)
            # Add more analysis functions here as the verifier grows
            index_error_score = self._check_for_potential_index_errors(tree)

            # Combine scores (for now, we only have one)
            final_score = index_error_score
            results["verifiability_score"] = final_score

        except SyntaxError as e:
            self.logger.warning(f"Verifier: SyntaxError - {e}. Returning lowest score.")
            results["verifiability_score"] = 0.0
        except Exception as e:
            self.logger.error(f"Verifier: An unexpected error occurred during analysis: {e}")
            results["verifiability_score"] = 0.1 # Penalize unexpected analysis errors

        return results
