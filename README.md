# Check-Mapping Repository

This repository provides tools to validate mappings to fragility models. It is designed for efficient processing of JSON schemas and fragility databases, ensuring accurate mapping and identifying unmapped items.

## Features

### **Schema Validation**
- Validate combinations generated from JSON schemas using the `schema_mapping_validator` module.
- Parallelize processing for efficient validation.
- Save results in structured JSON files for analysis.

### **Fragility Mapping Analysis**
- Analyze fragility databases to find mapped and unmapped IDs using the `fragility_mapping_checker` module.
- Count unique model IDs from valid results.
- Save summaries of mapped and unmapped fragility IDs for further evaluation.

### **Mapping Execution**
- Dynamically execute mapping scripts on AIM data using the `run_mapping.py` module.
- Validate AIM data and display results as pandas DataFrames.

### **Schema Combination Generation**
- Generate exhaustive combinations of schema properties using the `json_schema_combinator` module.
- Extract and validate property types and constraints.
- Support JSON Schema constraints such as `enum`, `minimum`, and `maximum`.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd check-mapping
   ```
2. Ensure you have Python 3.x installed.
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Modules Overview

### `run_mapping.py`
- **Purpose:** Execute a specified mapping function on AIM data.
- **Features:**
  - Dynamically imports mapping scripts and functions.
  - Validates AIM data against predefined schemas.
  - Supports both command-line and programmatic usage.
- **Example Command-Line Usage:**
  ```bash
  python run_mapping.py AIM.json /path/to/mapping_IM.py mapping
  ```

### `json_schema_combinator`
- **Purpose:** Generate all possible combinations of property values defined in a JSON schema.
- **Features:**
  - Extract types and constraints from JSON schemas.
  - Generate combinations using Cartesian product.
- **Example Programmatic Usage:**
  ```python
  from json_schema_combinator import extract_types_and_values, generate_combinations

  schema = {...}  # JSON schema definition
  types_and_values = extract_types_and_values(schema)
  combinations = generate_combinations(types_and_values)
  print(combinations)
  ```

### `schema_mapping_validator`
- **Purpose:** Validate and map combinations of input data derived from a JSON schema.
- **Features:**
  - Parallel processing with `multiprocessing` or `concurrent.futures`.
  - Tracks valid and invalid combinations, including errors and tracebacks.
- **Example Usage:**
  ```bash
  python schema_mapping_validator.py
  ```

### `fragility_mapping_checker`
- **Purpose:** Analyze fragility databases to identify mapped and unmapped IDs.
- **Features:**
  - Count unique model IDs and their occurrences from valid results.
  - Check whether fragility model IDs in the database are mapped.
- **Example Command-Line Usage:**
  ```bash
  python fragility_mapping_checker.py valid_results.json fragility_database.csv
  ```

## Usage

### 1. Run Schema Mapping Validation
Execute the schema mapping validation process using the Jupyter Notebook:
```bash
schema_mapping_demo.ipynb
```

### 2. Review Outputs
All results are saved in the `output_files` directory:
- `valid_combinations.json`: Valid combinations.
- `invalid_combinations.json`: Invalid combinations.
- `model_id_counts.json`: Unique model ID counts.
- `fragility_mapping_summary.json`: Summary of mapped IDs.
- `unmapped_model_ids.json`: List of unmapped model IDs.

### 3. Example Workflow
1. Open and run the `schema_mapping_demo.ipynb` notebook in Jupyter.
2. Review the outputs saved in the `output_files` directory:
   - Check valid and invalid combinations.
   - Analyze the summary of mapped and unmapped IDs.
3. Use the outputs to refine your mappings or schema definitions.

## Contribution Guidelines

We welcome contributions! Here's how you can help:
1. Report bugs or issues via the GitHub issues tab.
2. Submit pull requests to improve existing scripts or add new features.
3. Suggest improvements for documentation.

### Development Setup
1. Fork the repository and clone your fork:
   ```bash
   git clone <your-fork-url>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Test your changes using the Jupyter Notebook or new scripts.

Please follow the existing code style and structure for consistency.

## License

This repository is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Feel free to reach out if you have questions or suggestions!

