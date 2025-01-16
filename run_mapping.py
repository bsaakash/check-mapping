"""
This script is a utility to execute a specified mapping function on an AIM JSON file.

The script:
1. Accepts the path to the AIM JSON file, the full path to the mapping script, and the name of the mapping function as arguments.
2. Dynamically imports the mapping script and function.
3. Loads the AIM JSON file and validates it against the mapping function.
4. Displays the resulting component assignment (comp) as a pandas DataFrame.
5. Returns the comp DataFrame for further use.

Usage:
    python run_mapping.py <AIM_file_path> <mapping_script_path> <mapping_function_name>

Example:
    python run_mapping.py AIM.json /path/to/mapping_IM.py mapping

Requirements:
    - The mapping script must be a valid Python file.
    - The mapping function must accept a dictionary as input and return gi, dl_ap, and comp.
"""

import json
from pathlib import Path
import importlib.util
import argparse
import sys


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Run mapping function with specified inputs."
    )
    parser.add_argument("aim_file_path", type=str, help="Path to the AIM JSON file.")
    parser.add_argument(
        "mapping_script_path", type=str, help="Full path to the mapping script."
    )
    parser.add_argument(
        "mapping_function_name",
        type=str,
        help="Name of the mapping function to call.",
    )

    # Parse arguments
    args = parser.parse_args()

    aim_file_path = Path(args.aim_file_path)
    mapping_script_path = Path(args.mapping_script_path)
    mapping_function_name = args.mapping_function_name

    # Check if the AIM file exists
    if not aim_file_path.exists():
        print(f"Error: {aim_file_path} does not exist.")
        return

    # Check if the mapping script exists
    if not mapping_script_path.exists():
        print(f"Error: {mapping_script_path} does not exist.")
        return

    # Add the directory containing the mapping script to the Python path
    sys.path.insert(0, str(mapping_script_path.parent))

    # Dynamically import the mapping script and function
    try:
        spec = importlib.util.spec_from_file_location(
            "mapping_module", str(mapping_script_path)
        )
        mapping_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mapping_module)
        mapping_function = getattr(mapping_module, mapping_function_name)
    except ModuleNotFoundError as e:
        print(f"Error: Failed to import module from '{mapping_script_path}'.\n{e}")
        return
    except AttributeError as e:
        print(
            f"Error: Function '{mapping_function_name}' not found in module '{mapping_script_path}'.\n{e}"
        )
        return

    # Load the AIM.json file
    try:
        with aim_file_path.open("r", encoding="utf-8") as file:
            aim_data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse {aim_file_path} as JSON.\n{e}")
        return

    # Call the mapping function and handle any exceptions
    try:
        gi, dl_ap, comp = mapping_function(aim_data)
    except ValueError as e:
        print(f"Error during {mapping_function_name} execution:\n{e}")
        return

    # Display the comp DataFrame
    print("Component Assignment:")
    print(comp)

    # Return comp as the output
    return comp


if __name__ == "__main__":
    main()
