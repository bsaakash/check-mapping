"""
Module: mapping_combinations

This module facilitates validating and mapping all possible combinations of input data
derived from a JSON schema. It uses multiprocessing to parallelize the analysis and outputs
a summary of valid and invalid combinations.

Key Functions:
- run_combination: Validates and maps a single combination of input data.
- process_combinations: Orchestrates the validation and mapping for all combinations
generated from a given JSON schema.

Features:
- JSON schema validation using `jsonschema`.
- Parallel processing with Python's `multiprocessing`.
- Detailed tracking of valid and invalid combinations, including errors and tracebacks.
- Saves results to JSON files for further analysis.

Example Usage:
    Run the module as a script to process a mapping script and JSON schema:
    python mapping_combinations.py
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
        gi = aim_data['GeneralInformation']
        try:
            validate(instance=gi, schema=input_schema)
        except jsonschema.exceptions.ValidationError as exc:
            msg = ('The provided building information does not conform to the input'
                   ' requirements for the chosen damage and loss model.')
            return {
                'status': 'invalid',
                'combination': gi,
                'error': msg,
                'traceback': traceback.format_exc()
            }

        # Run the mapping function with the validated aim_data
        comp = run_mapping(aim_data, mapping_script, mapping_function)

        # Extract the model_id from the index of the comp DataFrame
        model_id = comp.index[0] if not comp.empty else None

        return {'status': 'valid', 'combination': gi, 'model_id': model_id}
    except Exception as e:
        return {
            'status': 'invalid',
            'combination': aim_data['GeneralInformation'],
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def process_combinations(mapping_script, mapping_function, json_schema_file):
    """
    Runs the mapping function for every combination derived from the JSON schema using multiprocessing.

    Args:
        mapping_script (str): Path to the mapping script to execute.
        mapping_function (str): Name of the mapping function to call.
        json_schema_file (str): Path to the JSON schema file defining the types and their possible values.

    Returns:
        dict: A dictionary with two keys:
            - 'valid': List of valid combinations with their corresponding model_id.
            - 'invalid': List of invalid combinations with errors.
    """
    # Load JSON schema from file
    with open(json_schema_file, "r") as schema_file:
        json_schema = json.load(schema_file)

    # Extract types and values from the JSON schema
    types_and_values = extract_types_and_values(json_schema)

    # Generate all possible combinations
    combinations = generate_combinations(types_and_values)

    # Prepare multiprocessing inputs with aim_data structure
    inputs = [
        ({"GeneralInformation": combination}, mapping_script, mapping_function, json_schema)
        for combination in combinations
    ]

    results = {
        'valid': [],
        'invalid': []
    }

    # Use multiprocessing Pool for parallel execution
    with Pool() as pool:
        outcomes = pool.map(run_combination, inputs)

    # Aggregate results
    for outcome in outcomes:
        if outcome['status'] == 'valid':
            results['valid'].append({
                'combination': outcome['combination'],
                'model_id': outcome['model_id']
            })
        else:
            results['invalid'].append({
                'combination': outcome['combination'],
                'error': outcome['error'],
                'traceback': outcome['traceback']
            })

    return results

if __name__ == "__main__":
    import time

    # Example usage
    mapping_script = "mapping_modules/HAZUS_EQ/mapping_IM.py"
    mapping_function = "auto_populate"
    json_schema_file = "mapping_modules/HAZUS_EQ/input_schema.json"

    start_time = time.time()
    results = process_combinations(mapping_script, mapping_function, json_schema_file)
    elapsed_time = time.time() - start_time

    # Summary
    total_combinations = len(results['valid']) + len(results['invalid'])
    print("\nSummary:")
    print(f"Total combinations: {total_combinations}")
    print(f"Valid combinations: {len(results['valid'])}")
    print(f"Invalid combinations: {len(results['invalid'])}")
    print(f"Time taken: {elapsed_time:.2f} seconds")

    # Save results to JSON
    with open("valid_combinations.json", "w") as valid_file:
        json.dump(results['valid'], valid_file, indent=4)
    with open("invalid_combinations.json", "w") as invalid_file:
        json.dump(results['invalid'], invalid_file, indent=4)
