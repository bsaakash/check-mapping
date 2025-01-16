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
        raise FileNotFoundError(f"Error: {mapping_script_path} does not exist.")

    # Add the directory containing the mapping script to the Python path
    sys.path.insert(0, str(mapping_script_path.parent))

    # Dynamically import the mapping script and function
    try:
        spec = importlib.util.spec_from_file_location(
            "mapping_module", str(mapping_script_path)
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec from {mapping_script_path}")
        mapping_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mapping_module)
        mapping_function = getattr(mapping_module, mapping_function_name)
    except ImportError as e:
        raise ImportError(
            f"Error: Failed to import module from '{mapping_script_path}'.\n{e}"
        )
    except AttributeError as e:
        raise ImportError(
            f"Error: Function '{mapping_function_name}' not found in module '{mapping_script_path}'.\n{e}"
        )

    # Call the mapping function and handle any exceptions
    try:
        gi, dl_ap, comp = mapping_function(aim_data)
    except Exception as e:  # Catch all exceptions for better debugging
        print(f"Error during {mapping_function_name} execution: {e}")
        raise

    return comp

def run_from_command_line():
    """
    Executes the mapping function using command-line arguments.
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
        print(f"Error: {aim_file_path} does not exist.")
        return

    # Load the AIM.json file
    try:
        with aim_file_path.open("r", encoding="utf-8") as file:
            aim_data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse {aim_file_path} as JSON.\n{e}")
        return

    # Run the mapping
    try:
        comp = run_mapping(aim_data, args.mapping_script_path, args.mapping_function_name)
        print("Component Assignment:")
        print(comp)
    except (FileNotFoundError, ImportError, ValueError) as e:
        print(e)

if __name__ == "__main__":
    run_from_command_line()
