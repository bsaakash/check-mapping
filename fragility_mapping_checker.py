"""
Module: fragility_mapping_checker

This module processes a fragility database provided as a CSV file. It allows users to:
- Count unique model IDs and their occurrences from valid results.
- Check if fragility model IDs in the CSV have been mapped to.

Key Functions:
- count_model_ids: Counts unique model IDs and their occurrences in the valid results.
- check_fragility_mapping: Checks each fragility model ID in the CSV to determine if it has been mapped to.

Features:
- Processes fragility database CSV files.
- Outputs whether each fragility model ID has been mapped to.
- Provides a summary of mapped and unmapped fragility model IDs.
- Saves results to JSON files for further analysis.

Example Usage:
    Run the module to check mapping of fragility model IDs:
    python fragility_mapping_checker.py valid_results.json fragility_database.csv
"""

import csv
import json
import time
from collections import Counter


def count_model_ids(valid_results, output_file):
    """
    Count unique model IDs and their occurrences in valid results and save to file.

    Args:
        valid_results (list): List of valid combinations with their model IDs.
        output_file (str): Path to save the model ID counts as a JSON file.

    Returns:
        dict: Dictionary with model_id as key and its count as value.
    """
    model_ids = [entry["model_id"] for entry in valid_results]
    model_id_counts = dict(Counter(model_ids))

    # Save model_id_counts to file
    with open(output_file, "w") as json_file:
        json.dump(model_id_counts, json_file, indent=4)

    return model_id_counts


def check_fragility_mapping(valid_results, fragility_csv, output_file):
    """
    Check if fragility model IDs in the CSV have been mapped to and provide a summary.

    Args:
        valid_results (list): List of valid combinations with their model IDs.
        fragility_csv (str): Path to the fragility database CSV file.
        output_file (str): Path to save the mapping results as a JSON file.

    Returns:
        dict: Summary of mapped and unmapped fragility model IDs, along with the list of unmapped IDs.
    """
    # Extract model IDs from valid results
    model_id_counts = count_model_ids(valid_results, "model_id_counts.json")
    mapped_model_ids = set(model_id_counts.keys())

    # Process the fragility CSV file
    fragility_status = []
    mapped_ids = []
    unmapped_ids = []
    with open(fragility_csv, "r") as csv_file:
        reader = csv.reader(csv_file)
        _ = next(reader)  # Skip the header row
        for row in reader:
            fragility_id = row[0]  # The fragility model ID is in the first column
            is_mapped = fragility_id in mapped_model_ids
            fragility_status.append(
                {"fragility_model_id": fragility_id, "is_mapped": is_mapped}
            )
            if is_mapped:
                mapped_ids.append(fragility_id)
            else:
                unmapped_ids.append(fragility_id)

    # Count mapped and unmapped IDs
    mapped_count = len(mapped_ids)
    unmapped_count = len(unmapped_ids)

    # Save results to file
    with open(output_file, "w") as json_file:
        json.dump(fragility_status, json_file, indent=4)

    # Return summary
    return {
        "total_fragility_ids": len(fragility_status),
        "mapped": mapped_count,
        "unmapped": unmapped_count,
        "mapped_ids": mapped_ids,
        "unmapped_ids": unmapped_ids,
    }


if __name__ == "__main__":
    import sys

    # Example usage
    if len(sys.argv) != 4:
        print(
            "Usage: python fragility_mapping_checker.py <valid_results.json> <fragility_database.csv> <output_file.json>"
        )
        sys.exit(1)

    valid_results_file = sys.argv[1]
    fragility_csv = sys.argv[2]
    output_file = sys.argv[3]

    # Load valid results
    with open(valid_results_file, "r") as f:
        valid_results = json.load(f)

    # Measure elapsed time
    start_time = time.time()

    # Check fragility mapping
    summary = check_fragility_mapping(valid_results, fragility_csv, output_file)

    elapsed_time = time.time() - start_time

    # Display summary
    print("\nFragility Mapping Summary:")
    print(f"Total fragility model IDs: {summary['total_fragility_ids']}")
    print(f"Mapped fragility model IDs: {summary['mapped']}")
    print(f"Unmapped fragility model IDs: {summary['unmapped']}")
    print("\nUnmapped IDs:")
    for unmapped_id in summary["unmapped_ids"]:
        print(unmapped_id)
    print(f"\nTime elapsed: {elapsed_time:.2f} seconds")
