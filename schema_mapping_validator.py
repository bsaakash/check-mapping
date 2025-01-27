"""
Module: schema_mapping_validator

This module facilitates the validation and mapping of all possible combinations of input data
derived from a JSON schema. It uses Python's `multiprocessing` module to parallelize the analysis
by default, with an option to execute in series for debugging or smaller datasets.

Key Features:
- **JSON Schema Validation**:
    - Validates input data combinations against a JSON schema using the `jsonschema` library.
- **Mapping Function Execution**:
    - Executes a user-specified mapping function to process valid combinations.
- **Parallel or Series Execution**:
    - Runs the validation and mapping in parallel using `multiprocessing` for efficiency.
    - Provides an option to execute in series for easier debugging or when parallelization is unnecessary.
- **Error Tracking**:
    - Captures detailed error messages and tracebacks for invalid combinations.
- **Result Storage**:
    - Outputs valid and invalid combinations as JSON files for further analysis.

Key Functions:
- `run_combination`:
    Validates and processes a single combination of input data.
- `process_combinations`:
    Orchestrates the validation and mapping for all combinations generated from a given JSON schema.
    Supports parallel or series execution.
- `main`:
    Command-line entry point to process a mapping script and JSON schema.

Example Usage:
    Run the module as a script to validate and map all possible combinations:

    python schema_mapping_validator.py

    Example arguments (within the script):
    - `mapping_script`: Path to the Python script containing the mapping function.
    - `mapping_function`: Name of the mapping function to call.
    - `json_schema_file`: Path to the JSON schema file defining input combinations.

Outputs:
- `valid_combinations.json`: Contains all valid combinations along with the extracted model IDs.
- `invalid_combinations.json`: Contains all invalid combinations with detailed error messages and tracebacks.

Dependencies:
- `multiprocessing`: For parallel execution.
- `jsonschema`: For schema validation.
- `run_mapping`: User-defined module to execute mapping functions.
- `json_schema_combinator`: Generates all possible combinations from the JSON schema.

This module is ideal for use cases such as automated testing, input validation, and scenario analysis
where exhaustive combinations of input data need to be validated and processed.
"""

from run_mapping import run_mapping
from json_schema_combinator import generate_combinations, extract_types_and_values
import json
import time
from multiprocessing import Pool
import traceback
from jsonschema import validate
import jsonschema.exceptions


def run_combination(args):
    """
    Helper function to run a mapping for a single combination.
    """
    aim_data, mapping_script, mapping_function, input_schema = args
    try:
        # Validate the provided features against the required inputs
        gi = aim_data["GeneralInformation"]
        try:
            validate(instance=gi, schema=input_schema)
        except jsonschema.exceptions.ValidationError:
            msg = (
                "The provided building information does not conform to the input"
                " requirements for the chosen damage and loss model."
            )
            return {
                "status": "invalid",
                "combination": gi,
                "error": msg,
                "traceback": traceback.format_exc(),
            }

        # Run the mapping function with the validated aim_data
        comp = run_mapping(aim_data, mapping_script, mapping_function)

        # Extract all model_ids from the index of the comp DataFrame
        if not comp.empty:
            model_ids = comp.index.tolist()
        else:
            model_ids = []

        return {"status": "valid", "combination": gi, "model_ids": model_ids}
    except Exception as e:
        return {
            "status": "invalid",
            "combination": aim_data["GeneralInformation"],
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


def process_combinations(
    mapping_script, mapping_function, json_schema_file, parallel=True
):
    """
    Runs the mapping function for every combination derived from the JSON schema.

    Args:
        mapping_script (str): Path to the mapping script to execute.
        mapping_function (str): Name of the mapping function to call.
        json_schema_file (str): Path to the JSON schema file defining the types and their possible values.
        parallel (bool): Whether to use multiprocessing (True) or run in series (False).

    Returns:
        dict: A dictionary with two keys:
            - 'valid': List of valid combinations with their corresponding model_id.
            - 'invalid': List of invalid combinations with errors.
    """
    # Load JSON schema from file
    with open(json_schema_file, "r") as schema_file:
        json_schema = json.load(schema_file)

    # Extract types and values from the JSON schema
    types_and_values, required = extract_types_and_values(json_schema)

    # Generate all possible combinations
    combinations = generate_combinations(types_and_values, required)

    # Prepare inputs with aim_data structure
    inputs = [
        (
            {"GeneralInformation": combination},
            mapping_script,
            mapping_function,
            json_schema,
        )
        for combination in combinations
    ]

    results = {"valid": [], "invalid": []}

    if parallel:
        # Use multiprocessing Pool for parallel execution
        with Pool() as pool:
            outcomes = pool.map(run_combination, inputs)
    else:
        # Run in series
        outcomes = [run_combination(args) for args in inputs]

    # Aggregate results
    for outcome in outcomes:
        if outcome["status"] == "valid":
            results["valid"].append(
                {
                    "combination": outcome["combination"],
                    "model_ids": outcome["model_ids"],
                }
            )
        else:
            results["invalid"].append(
                {
                    "combination": outcome["combination"],
                    "error": outcome["error"],
                    "traceback": outcome["traceback"],
                }
            )

    return results


if __name__ == "__main__":
    # Example usage
    mapping_script = "mapping_modules/HAZUS_EQ/mapping_IM.py"
    mapping_function = "auto_populate"
    json_schema_file = "mapping_modules/HAZUS_EQ/input_schema.json"

    start_time = time.time()
    # Toggle between parallel and series execution with the `parallel` argument
    results = process_combinations(
        mapping_script, mapping_function, json_schema_file, parallel=True
    )
    elapsed_time = time.time() - start_time

    # Summary
    total_combinations = len(results["valid"]) + len(results["invalid"])
    print("Summary:")
    print(f"Total combinations: {total_combinations}")
    print(f"Valid combinations: {len(results['valid'])}")
    print(f"Invalid combinations: {len(results['invalid'])}")
    print(f"Time taken: {elapsed_time:.2f} seconds")

    # Save results to JSON
    with open("valid_combinations.json", "w") as valid_file:
        json.dump(results["valid"], valid_file, indent=4)
    with open("invalid_combinations.json", "w") as invalid_file:
        json.dump(results["invalid"], invalid_file, indent=4)
