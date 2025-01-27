"""
run_mapping.py

This module provides utilities to execute a specified mapping function on AIM data.

The module contains two primary functions:
1. `run_mapping`: Executes a mapping function on AIM data provided as a Python dictionary.
2. `run_from_command_line`: A command-line interface to execute the mapping function using an AIM JSON file.

Features:
- Dynamically imports a specified mapping script and function.
- Validates the provided AIM data.
- Displays the resulting component assignment as a pandas DataFrame.

Usage:
    Command-Line:
        python run_mapping.py <AIM_file_path> <mapping_script_path> <mapping_function_name>
    Programmatic:
        from this_module import run_mapping
        comp = run_mapping(aim_data, mapping_script_path, mapping_function_name)

Example:
    Command-Line:
        python run_mapping.py AIM.json /path/to/mapping_IM.py mapping
    Programmatic:
        comp = run_mapping(aim_data, '/path/to/mapping_IM.py', 'mapping')

Requirements:
    - The mapping script must be a valid Python file.
    - The mapping function must accept a dictionary as input and return gi, dl_ap, and comp.
    - The AIM data must conform to the expected schema.

Exceptions:
    - Raises FileNotFoundError if the mapping script is not found.
    - Raises ImportError if the script or function cannot be imported.
    - Raises ValueError for validation or execution errors.

"""

import json
from pathlib import Path
import importlib.util
import sys
import argparse


def run_mapping(aim_data, mapping_script_path, mapping_function_name):
    """
    Executes the mapping function on the provided AIM data.

    Args:
        aim_data (dict): The AIM data as a Python dictionary.
        mapping_script_path (str or Path): Full path to the mapping script.
        mapping_function_name (str): Name of the mapping function to call.

    Returns:
        pandas.DataFrame: The component assignment (comp) as a DataFrame.

    Raises:
        FileNotFoundError: If the mapping script does not exist.
        ImportError: If the mapping script or function cannot be imported.
        ValueError: If there is an error during the execution of the mapping function.
    """
    mapping_script_path = Path(mapping_script_path)

    # Check if the mapping script exists
    if not mapping_script_path.exists():
        raise FileNotFoundError(f"{mapping_script_path} does not exist.")

    # Add the directory containing the mapping script to the Python path
    sys.path.insert(0, str(mapping_script_path.parent))

    # Dynamically import the mapping script and function
    try:
        spec = importlib.util.spec_from_file_location(
            "mapping_module", str(mapping_script_path)
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec from {mapping_script_path}.")
        mapping_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mapping_module)
        mapping_function = getattr(mapping_module, mapping_function_name)
    except ImportError as e:
        raise ImportError(
            f"Failed to import module from '{mapping_script_path}'.\nDetails: {e}"
        )
    except AttributeError as e:
        raise ImportError(
            f"Function '{mapping_function_name}' not found in module '{mapping_script_path}'.\nDetails: {e}"
        )

    # Call the mapping function and handle any exceptions
    try:
        gi, dl_ap, comp = mapping_function(aim_data)
    except Exception as e:
        raise ValueError(
            f"Error occurred during execution of function '{mapping_function_name}': {e}"
        )

    return comp


def run_from_command_line():
    """
    Executes the mapping function using command-line arguments.

    Raises:
        FileNotFoundError: If the specified AIM file does not exist.
        json.JSONDecodeError: If the AIM file is not valid JSON.
        FileNotFoundError, ImportError, ValueError: If errors occur during mapping.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Run mapping function with specified inputs."
    )
    parser.add_argument("aim_file_path", type=str, help="Path to the AIM JSON file.")
    parser.add_argument(
        "mapping_script_path", type=str, help="Full path to the mapping script."
    )
    parser.add_argument(
        "mapping_function_name", type=str, help="Name of the mapping function to call."
    )

    # Parse arguments
    args = parser.parse_args()

    aim_file_path = Path(args.aim_file_path)

    # Check if the AIM file exists
    if not aim_file_path.exists():
        raise FileNotFoundError(f"{aim_file_path} does not exist.")

    # Load the AIM.json file
    try:
        with aim_file_path.open("r", encoding="utf-8") as file:
            aim_data = json.load(file)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Failed to parse {aim_file_path} as JSON.", doc=e.doc, pos=e.pos
        )

    # Run the mapping
    try:
        comp = run_mapping(
            aim_data, args.mapping_script_path, args.mapping_function_name
        )
        print("Component Assignment:")
        print(comp)
    except (FileNotFoundError, ImportError, ValueError) as e:
        raise RuntimeError(
            f"An error occurred during the mapping process:\n{e}"
        ) from e


if __name__ == "__main__":
    try:
        run_from_command_line()
    except Exception as e:
        # Provide a top-level catch for uncaught exceptions
        print(f"Fatal error: {e}")
        sys.exit(1)
