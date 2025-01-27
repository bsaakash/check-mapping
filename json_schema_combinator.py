"""
json_schema_combinator

This module provides functionality to parse a JSON Schema and generate all valid combinations
of property values based on the schema's constraints. It ensures that required properties are
always included in every combination while optional properties can be included or excluded,
representing both their presence and absence in the combinations.

Key Features:
- Extract property types and supported values from a JSON Schema, including handling `enum`, `type`,
  and required fields.
- Generate combinations of property values using Cartesian product, ensuring required properties
  are always included and optional properties can be excluded (represented as None).
- Filter combinations to ensure validity with respect to the schema.

Typical Usage Example:
    # Load a JSON schema
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "BuildingType": {
                "type": "string",
                "enum": ["W1", "W2", "S1", "S2", "S3"]
            },
            "DesignLevel": {
                "type": "string",
                "enum": ["Pre-Code", "Low-Code"]
            },
            "HeightClass": {
                "type": "string",
                "enum": ["Low-Rise", "Mid-Rise"]
            },
            "GroundFailure": {"type": "boolean"}
        },
        "required": ["BuildingType", "DesignLevel"]
    }

    # Extract property types and values
    types_and_values, required = extract_types_and_values(schema)

    # Generate all valid combinations of property values
    combinations = generate_combinations(types_and_values, required)

    # Example output
    print(combinations)

Module Functions:
- extract_types_and_values(schema):
    Parses the JSON schema and extracts a dictionary of property names, their types, and supported values.
    Also identifies required properties.

- generate_combinations(types_and_values, required):
    Generates all valid combinations of property values, ensuring required properties are always present,
    and optional properties can be excluded.

This module is ideal for scenarios such as testing, simulation, or validation where exhaustive combinations
of property values defined by a JSON schema are needed.
"""

import itertools


def extract_types_and_values(schema):
    """
    Extract types and supported values from a JSON schema.

    Args:
        schema (dict): The JSON schema dictionary.

    Returns:
        tuple: A dictionary with property names as keys and their types and supported values as values,
               and a set of required properties.
    """
    types_and_values = {}
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    for prop, details in properties.items():
        prop_type = details.get("type", "unknown")
        values = []

        if "enum" in details:  # For enumerated values
            values = details["enum"]
        elif prop_type == "boolean":
            values = [True, False]
        elif prop_type == "string":
            values = ["example_string"]
        else:
            values = [f"default_{prop_type}"]

        # Optional properties can also have a "None" value to signify exclusion
        if prop not in required:
            values = [None] + values

        types_and_values[prop] = {"type": prop_type, "values": values}

    return types_and_values, required


def generate_combinations(types_and_values, required):
    """
    Generate all combinations of the values of the properties.

    Args:
        types_and_values (dict): A dictionary containing types and values of properties.
        required (set): A set of required property names.

    Returns:
        list: A list of dictionaries, each representing a unique combination of property values.
    """
    keys = types_and_values.keys()
    value_lists = [types_and_values[key]["values"] for key in keys]

    # Generate all possible combinations
    all_combinations = list(itertools.product(*value_lists))

    # Filter combinations to ensure required properties are present
    valid_combinations = []
    for combination in all_combinations:
        combo_dict = dict(zip(keys, combination))

        # Ensure all required properties are present and not None
        if all(combo_dict[key] is not None for key in required):
            # Remove optional properties that are None
            valid_combinations.append(
                {k: v for k, v in combo_dict.items() if v is not None}
            )

    return valid_combinations


# Example Usage
if __name__ == "__main__":
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "BuildingType": {
                "type": "string",
                "enum": [
                    "W1",
                    "W2",
                    "S1",
                    "S2",
                    "S3",
                    "S4",
                    "S5",
                    "C1",
                    "C2",
                    "C3",
                    "PC1",
                    "PC2",
                    "RM1",
                    "RM2",
                    "URM",
                    "MH",
                ],
            },
            "DesignLevel": {
                "type": "string",
                "enum": ["Pre-Code", "Low-Code", "Moderate-Code", "High-Code"],
            },
            "HeightClass": {
                "type": "string",
                "enum": ["Low-Rise", "Mid-Rise", "High-Rise"],
            },
            "GroundFailure": {"type": "boolean"},
            "FoundationType": {"type": "string", "enum": ["Shallow", "Deep"]},
            "OccupancyClass": {
                "type": "string",
                "enum": [
                    "RES1",
                    "RES2",
                    "RES3",
                    "RES4",
                    "RES5",
                    "RES6",
                    "COM1",
                    "COM2",
                    "COM3",
                    "COM4",
                    "COM5",
                    "COM6",
                    "COM7",
                    "COM8",
                    "COM9",
                    "COM10",
                    "IND1",
                    "IND2",
                    "IND3",
                    "IND4",
                    "IND5",
                    "IND6",
                    "AGR1",
                    "REL1",
                    "GOV1",
                    "GOV2",
                    "EDU1",
                    "EDU2",
                ],
            },
        },
        "required": ["BuildingType", "DesignLevel"],
    }

    types_and_values, required = extract_types_and_values(schema)
    combinations = generate_combinations(types_and_values, required)

    print("Extracted Types and Values:")
    for prop, info in types_and_values.items():
        print(
            f"- {prop} ({info['type']}): {len(info['values'])} values: {info['values']}"
        )

    print("\nGenerated Combinations:")
    print(f"Total combinations: {len(combinations)}")
    for combo in combinations[:5]:  # Print the first 5 combinations for brevity
        print(combo)
