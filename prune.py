import json
import os
import configparser
import argparse
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Define default values for certain variables
DEFAULT_INPUT_DIR = "./input"
DEFAULT_OUTPUT_DIR = "./pruned"

# Create the argument parser
parser = argparse.ArgumentParser()

# Add arguments for the input directory, input JSON file, and output directory
parser.add_argument("--input_dir", type=str, default=DEFAULT_INPUT_DIR, help="Path to the directory containing images")
parser.add_argument("--input_json", type=str, default="./output/results.json", help="Path to the JSON file")
parser.add_argument("--output_dir", type=str, default=DEFAULT_OUTPUT_DIR, help="Path to the output directory")

# Parse the arguments
args = parser.parse_args()

# Load the JSON file
with open(args.input_json, "r") as f:
    results = json.load(f)

# Load the pruning configuration
config = configparser.ConfigParser()
config.read('pruneconfig.ini')

# Ensure PRUNING_RULES section exists
if 'PRUNING_RULES' not in config:
    raise ValueError("Missing [PRUNING_RULES] section in pruneconfig.ini")

# Convert the pruning conditions from percentages to decimals
prune_conditions = {}
for key in config['PRUNING_RULES']:
    condition = config['PRUNING_RULES'][key].strip()
    if condition:
        # Ensure there's a space between the operator and the value
        if condition[0] in ('>', '<', '='):
            # Check if there's a space between the operator and the value
            if len(condition) > 1 and condition[1] != ' ':
                condition = condition[0] + ' ' + condition[1:]
        try:
            op, value = condition.split()
            prune_conditions[key] = (op, float(value) / 100)
        except ValueError as e:
            print(f"Invalid condition '{condition}' for key '{key}': {e}")

# Map 'manga' to 'manga_like'
prune_conditions = {('manga_like' if k == 'manga' else k): v for k, v in prune_conditions.items()}

# Print prune configuration
print(Fore.CYAN + "Prune configuration:")
for key, condition in prune_conditions.items():
    print(f"  {key}: {condition[0]} {condition[1] * 100:.2f}%")
print("")

# Check if the output folder exists, if not create it
if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

# Load existing pruned files
pruned_file_path = os.path.join(args.output_dir, "pruned.json")
if os.path.exists(pruned_file_path):
    with open(pruned_file_path, "r") as f:
        existing_pruned_files = json.load(f)
else:
    existing_pruned_files = []

# Convert existing pruned files to a set of filenames for quick lookup
existing_pruned_filenames = {file["filename"] for file in existing_pruned_files}

# Function to evaluate a condition
def evaluate_condition(value, condition):
    if not condition:
        return True
    try:
        op, threshold = condition
        if op == ">":
            return value > threshold
        elif op == ">=":
            return value >= threshold
        elif op == "<":
            return value < threshold
        elif op == "<=":
            return value <= threshold
        elif op == "=":
            return value == threshold
    except ValueError as e:
        print(f"Error evaluating condition '{condition}': {e}")
    return True

# Iterate over the results
new_pruned_files = []
kept_files_count = 0
pruned_files_count = 0

for result in results:
    # Get the filename and scores
    filename = result["filename"]
    aesthetic_score = result["aesthetic"]["aesthetic"]
    style_scores = result["style"]
    waifu_score = result["waifu"]["waifu"]

    # Evaluate pruning conditions
    prune = False
    relevant_values = []

    if 'aesthetic' in prune_conditions:
        relevant_values.append(f"Aesthetic: {aesthetic_score * 100:.2f}%")
        if not evaluate_condition(aesthetic_score, prune_conditions['aesthetic']):
            prune = True

    for key in style_scores:
        if key in prune_conditions:
            relevant_values.append(f"{key}: {style_scores[key] * 100:.2f}%")
            if not evaluate_condition(style_scores[key], prune_conditions[key]):
                prune = True
                break

    if 'waifu' in prune_conditions:
        relevant_values.append(f"Waifu: {waifu_score * 100:.2f}%")
        if not evaluate_condition(waifu_score, prune_conditions['waifu']):
            prune = True

    source_path = os.path.join(args.input_dir, filename)
    target_path = os.path.join(args.output_dir, filename)
    target_dir = os.path.dirname(target_path)
    
    # Check if source file exists
    if not os.path.exists(source_path):
        print(Fore.YELLOW + f"Missing {filename}")
        continue

    if prune:
        # Create the target directory if it doesn't exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        os.rename(source_path, target_path)
        new_pruned_files.append(result)
        pruned_files_count += 1
        print(Fore.RED + f"\nPruned {filename}:")
    else:
        kept_files_count += 1
        print(Fore.GREEN + f"\nKept {filename}:")

    for value in relevant_values:
        print(f"  {value}")

# Combine new pruned files with existing pruned files
all_pruned_files = existing_pruned_files + new_pruned_files

# Save pruned files info to pruned.json
with open(pruned_file_path, "w") as f:
    json.dump(all_pruned_files, f, indent=2)

# Print summary
print(Fore.CYAN + "\n\nPruning completed.")
print(Fore.GREEN + f"Total files kept: {kept_files_count}")
print(Fore.RED + f"Total files pruned: {pruned_files_count}")
