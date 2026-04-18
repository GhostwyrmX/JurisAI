import sys
import os

# Add parent directory to path to import modules
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from utils.validation import validate_dataset

# Test the validation with the dataset path
dataset_path = os.path.join("..", "dataset/ipc/ipc.json")
print(f"Validating dataset at: {dataset_path}")
print(f"Current working directory: {os.getcwd()}")
print(f"Dataset file exists: {os.path.exists(dataset_path)}")

result = validate_dataset(dataset_path)
print(f"Validation result: {result}")