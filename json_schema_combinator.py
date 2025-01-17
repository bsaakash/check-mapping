"""
json_schema_combinator

This module provides functionality to extract property types and supported values from a JSON Schema
and generate all possible combinations of those property values.

Key Features:
- Parse a JSON Schema to extract the types and constraints for each property.
- Support various JSON Schema constraints such as `enum`, `minimum`, `maximum`, and `type`.
- Generate all combinations of property values using Cartesian product.

Typical Usage Example:
    # Load a JSON schema
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "BuildingType":{
                "type": "string",
                "enum": [
                    "W1", "W2",
                    "S1", "S2", "S3", "S4", "S5",
                    "C1", "C2", "C3",
                    "PC1", "PC2",
                    "RM1", "RM2", "URM",
                    "MH"
                ]
            },
            "DesignLevel":{
                "type": "string",
                "enum": [
                    "Pre-Code",
                    "Low-Code",
                    "Moderate-Code",
                    "High-Code"
                ]
            },
            "HeightClass":{
                "type": "string",
                "enum": [
                    "Low-Rise",
                    "Mid-Rise",
                    "High-Rise"
                ]
            },
            "GroundFailure": {
                "type": "boolean"
            },
            "FoundationType":{
                "type": "string",
                "enum": [
                    "Shallow",
                    "Deep"
                ]
            },
            "OccupancyClass": {
                "type": "string",
                "enum": [
                    "RES1","RES2","RES3","RES4","RES5","RES6",
                    "COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9","COM10",
                    "IND1","IND2","IND3","IND4","IND5","IND6",
                    "AGR1",
                    "REL1",
                    "GOV1","GOV2",
                    "EDU1","EDU2"
                ]
            }
        }
    }

    # Extract types and values
    types_and_values = extract_types_and_values(schema)

    # Generate all combinations
    combinations = generate_combinations(types_and_values)

    print(combinations)

This module is useful for testing, simulation, or validation scenarios where exhaustive combinations
of property values defined by a JSON schema are required.
"""

import itertools


def extract_types_and_values(schema):
    """
    Extract types and supported values from a JSON schema.

    Args:
        schema (dict): The JSON schema dictionary.

    Returns:
        dict: A dictionary with property names as keys and their types and supported values as values.
    """
    types_and_values = {}
    properties = schema.get("properties", {})

    for prop, details in properties.items():
        prop_type = details.get("type", "unknown")
        values = []

        if "enum" in details:  # For enumerated values
            values = details["enum"]
        # elif prop_type == "number" or prop_type == "integer":
        #     if "minimum" in details and "maximum" in details:
        #         # Generate a range of values (example: step of 1 for simplicity)
        #         values = list(range(details["minimum"], details["maximum"] + 1))
        #     elif "minimum" in details:
        #         values = [details["minimum"]]
        #     elif "maximum" in details:
        #         values = [details["maximum"]]
        elif prop_type == "string":
            if "enum" in details:
                values = details["enum"]
            else:
                values = ["example_string"]
        elif prop_type == "boolean":
            values = [True, False]

        # Fallback for unsupported types or missing constraints
        if not values:
            values = [f"default_{prop_type}"]

        types_and_values[prop] = {"type": prop_type, "values": values}

    return types_and_values


def generate_combinations(types_and_values):
    """
    Generate all combinations of the values of the properties.

    Args:
        types_and_values (dict): A dictionary containing types and values of properties.

    Returns:
        list: A list of dictionaries, each representing a unique combination of property values.
    """
    keys = types_and_values.keys()
    value_lists = [types_and_values[key]["values"] for key in keys]
    combinations = list(itertools.product(*value_lists))
    return [dict(zip(keys, combination)) for combination in combinations]


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
    }

    types_and_values = extract_types_and_values(schema)
    combinations = generate_combinations(types_and_values)

    print("Extracted Types and Values:")
    for prop, info in types_and_values.items():
        print(
            f"- {prop} ({info['type']}): {len(info['values'])} values: {info['values']}"
        )

    print("\nGenerated Combinations:")
    print(f"Total combinations: {len(combinations)}")
    for combo in combinations[:5]:  # Print the first 5 combinations for brevity
        print(combo)
