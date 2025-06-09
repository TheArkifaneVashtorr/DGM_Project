# fitness.py (Refactored for Sandbox Test Harness)
# This version evaluates code by building and running it in an isolated Docker container.

import ast
import time
import os
import uuid
import tempfile
import shutil
import docker
import config

def evaluate_fitness(generated_code: str, execution_time: float) -> tuple[float, str | None]:
    """
    Calculates fitness by running the generated code in an isolated Docker container.
    Returns a tuple of (fitness_score, error_message).
    """
    processed_code = generated_code.strip()

    if not processed_code or "ERROR:" in processed_code:
        return 0.0, "Generated code was empty or an error placeholder."

    # 1. Syntax Check (pre-computation check)
    try:
        ast.parse(processed_code)
    except (SyntaxError, ValueError) as e:
        error_msg = f"Pre-check Syntax Error: {e}"
        print(f"Fitness evaluation: {error_msg}")
        return 0.0, error_msg

    # Create a temporary directory to build the test container
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # --- Write generated code and test runner to temp directory ---
            with open(os.path.join(temp_dir, "test_subject.py"), "w") as f:
                f.write(processed_code)

            runner_script = (
                "from test_subject import example_function_to_refactor\n"
                "test_input = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\n"
                "try:\n"
                "    result = example_function_to_refactor(test_input)\n"
                "    print(result)\n"
                "except Exception as e:\n"
                "    print(f'EXECUTION_ERROR: {e}')\n"
            )
            with open(os.path.join(temp_dir, "run_test.py"), "w") as f:
                f.write(runner_script)

            dockerfile_content = (
                "FROM python:3.11-slim\n"
                "WORKDIR /test\n"
                "COPY . .\n"
                "CMD [\"python\", \"run_test.py\"]\n"
            )
            with open(os.path.join(temp_dir, "Dockerfile"), "w") as f:
                f.write(dockerfile_content)

            # --- Use Docker SDK to build and run the test ---
            client = docker.from_env()
            image_tag = f"dgm-test-run:{uuid.uuid4().hex}"
            
            print(f"--- Building test container: {image_tag} ---")
            image, _ = client.images.build(path=temp_dir, tag=image_tag, rm=True, forcerm=True)
            
            print(f"--- Running test container: {image_tag} ---")
            container = client.containers.run(image.id, detach=True)
            result = container.wait(timeout=30)
            logs = container.logs().decode('utf-8').strip()
            container.remove()

            # --- Evaluate the results from the container ---
            if result['StatusCode'] != 0 or "EXECUTION_ERROR:" in logs:
                error_msg = f"Execution Error inside container: {logs}"
                print(f"Fitness evaluation: {error_msg}")
                return 0.0, error_msg

            try:
                # The output from the container should be a string representation of a list
                actual_output = ast.literal_eval(logs)
                expected_output = [2, 4, 6, 8, 10]

                if actual_output != expected_output:
                    error_msg = f"Output Mismatch. Expected {expected_output}, but got {actual_output}."
                    print(f"Fitness evaluation: {error_msg}")
                    return 0.25, error_msg
                
                # SUCCESS
                success_msg = f"Semantic check PASSED. Output: {actual_output}"
                print(f"Fitness evaluation: {success_msg}")
                total_fitness = (config.FITNESS_WEIGHTS["correctness"] * 1.0) - (config.FITNESS_WEIGHTS["efficiency"] * (execution_time / 30.0))
                return max(0, total_fitness), None

            except (ValueError, SyntaxError):
                error_msg = f"Container output was not a valid Python literal: {logs}"
                print(f"Fitness evaluation: {error_msg}")
                return 0.0, error_msg

        except docker.errors.BuildError as e:
            error_msg = f"Container Build Error (likely bad code): {e}"
            print(f"Fitness evaluation: {error_msg}")
            return 0.0, error_msg
        except Exception as e:
            error_msg = f"Sandbox Harness Error: {e}"
            print(f"Fitness evaluation: {error_msg}")
            return 0.0, error_msg
