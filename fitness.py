# fitness.py (Refactored for Semantic Evaluation)
# Implements a more advanced fitness function that executes code to check for correctness.

import ast
import time
import config

def evaluate_fitness(generated_code: str, execution_time: float) -> float:
    """
    Calculates the fitness of a generated piece of code by executing it
    and comparing its output to a known correct result.

    A higher score is better.
    """
    # Immediately fail if code is empty or an error message.
    if not generated_code.strip() or "ERROR:" in generated_code:
        return 0.0

    # 1. Syntax Check (as before)
    try:
        ast.parse(generated_code)
    except (SyntaxError, ValueError):
        # ValueError can be raised for null bytes in code
        print("Fitness evaluation: Generated code has syntax errors.")
        return 0.0

    # 2. Semantic (Execution) Check 
    # We execute the generated code and check if the output is correct.
    correctness_score = 0.0
    try:
        # Define the expected output of the function we are trying to refactor.
        expected_output = [2, 4, 6, 8, 10]

        # Create a dictionary to serve as the execution scope.
        execution_scope = {}
        
        # Execute the generated string of Python code.
        # The string should contain the definition of the refactored function.
        exec(generated_code, execution_scope)

        # The generated code should have defined our target function.
        refactored_function = execution_scope.get('example_function_to_refactor')

        if callable(refactored_function):
            # Call the generated function and get its output.
            actual_output = refactored_function()
            if actual_output == expected_output:
                # The function works as expected. This is a highly fit individual.
                correctness_score = 1.0
                print(f"Fitness evaluation: Semantic check PASSED. Output: {actual_output}")
            else:
                # The function runs but produces the wrong output.
                correctness_score = 0.25 # Assign partial credit
                print(f"Fitness evaluation: Semantic check FAILED. Expected {expected_output}, got {actual_output}")
        else:
            # The code was valid syntax but did not define the required function.
            correctness_score = 0.1 # Assign minor credit for valid code
            print("Fitness evaluation: Code is valid but did not define 'example_function_to_refactor'.")

    except Exception as e:
        # The code was syntactically valid but failed at runtime.
        correctness_score = 0.0
        print(f"Fitness evaluation: Code failed during execution: {e}")

    # 3. Efficiency Penalty (as before)
    max_tolerable_time = 30.0
    efficiency_penalty = min(execution_time / max_tolerable_time, 1.0)

    # Combine scores
    total_fitness = (
        config.FITNESS_WEIGHTS["correctness"] * correctness_score -
        config.FITNESS_WEIGHTS["efficiency"] * efficiency_penalty
    )

    return max(0, total_fitness)
