from run_mapping import run_mapping
from json_schema_combinator import generate_combinations, extract_types_and_values
import json
from multiprocessing import Pool
import traceback

def run_combination(args):
    """
    Helper function to run a mapping for a single combination.
    """
    aim_data, mapping_script, mapping_function = args
    try:
        # Run the mapping function with the aim_data
        comp = run_mapping(aim_data, mapping_script, mapping_function)

        # Extract the model_id from the index of the comp DataFrame
        model_id = comp.index[0] if not comp.empty else None

        return {'status': 'valid', 'combination': aim_data['GeneralInformation'], 'model_id': model_id}
    except Exception as e:
        return {
            'status': 'invalid',
            'combination': aim_data['GeneralInformation'],
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def process_combinations(mapping_script, mapping_function, json_schema):
    """
    Runs the mapping function for every combination derived from the JSON schema using multiprocessing.

    Args:
        mapping_script (str): Path to the mapping script to execute.
        mapping_function (str): Name of the mapping function to call.
        json_schema (dict): A JSON schema defining the types and their possible values.

    Returns:
        dict: A dictionary with two keys:
            - 'valid': List of valid combinations with their corresponding model_id.
            - 'invalid': List of invalid combinations with errors.
    """
    # Extract types and values from the JSON schema
    types_and_values = extract_types_and_values(json_schema)

    # Generate all possible combinations
    combinations = generate_combinations(types_and_values)

    # Prepare multiprocessing inputs with aim_data structure
    inputs = [
        ({"GeneralInformation": combination}, mapping_script, mapping_function)
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
    # Example usage
    mapping_script = "mapping_modules/HAZUS_EQ/mapping_IM.py"
    mapping_function = "auto_populate"
    # Load JSON schema from file
    with open("mapping_modules/HAZUS_EQ/input_schema.json", "r") as schema_file:
        json_schema = json.load(schema_file)
    results = process_combinations(mapping_script, mapping_function, json_schema)

    # # Print valid and invalid results
    # print("Valid combinations:")
    # for valid in results['valid']:
    #     print(valid)

    # print("\nInvalid combinations:")
    # for invalid in results['invalid']:
    #     print(invalid)

    # Summary
    total_combinations = len(results['valid']) + len(results['invalid'])
    print("\nSummary:")
    print(f"Total combinations: {total_combinations}")
    print(f"Valid combinations: {len(results['valid'])}")
    print(f"Invalid combinations: {len(results['invalid'])}")

    # Save results to JSON
    with open("valid_combinations.json", "w") as valid_file:
        json.dump(results['valid'], valid_file, indent=4)
    with open("invalid_combinations.json", "w") as invalid_file:
        json.dump(results['invalid'], invalid_file, indent=4)
