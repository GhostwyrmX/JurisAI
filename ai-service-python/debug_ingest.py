import sys
import os
import traceback

# Add parent directory to path to import modules
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

print(f"Script directory: {script_dir}")
print(f"Parent directory: {parent_dir}")
print(f"Sys path: {sys.path}")

try:
    from utils.config import Config
    print(f"MONGO_URI: {Config.MONGO_URI}")
except Exception as e:
    print(f"Error importing Config: {e}")
    traceback.print_exc()

try:
    from utils.logging import log_info, log_error
    print("Logging module imported successfully")
except Exception as e:
    print(f"Error importing logging: {e}")
    traceback.print_exc()

try:
    from utils.validation import validate_dataset
    print("Validation module imported successfully")
except Exception as e:
    print(f"Error importing validation: {e}")
    traceback.print_exc()