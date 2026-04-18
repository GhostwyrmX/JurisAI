import sys
import os
import json
from pymongo import MongoClient

# Add parent directory to path to import modules
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from utils.config import Config
from utils.logging import log_info, log_error
from utils.validation import validate_dataset

def ingest_dataset_to_mongodb():
    """Ingest IPC dataset into MongoDB"""
    try:
        # Validate dataset first
        # Fix path when running from ai-service-python directory
        dataset_relative_path = Config.LEGAL_ACTS["IPC"]["dataset"]
        if os.getcwd().endswith("ai-service-python"):
            dataset_path = os.path.join("..", dataset_relative_path)
        else:
            dataset_path = os.path.join(os.getcwd(), dataset_relative_path)
            
        print(f"Looking for dataset at: {dataset_path}")
        print(f"Current working directory: {os.getcwd()}")
        
        if not os.path.exists(dataset_path):
            log_error(f"Dataset file not found at: {dataset_path}")
            print(f"Dataset file not found at: {dataset_path}")
            return False
            
        if not validate_dataset(dataset_path):
            log_error("Dataset validation failed. Aborting ingestion.")
            print("Dataset validation failed. Aborting ingestion.")
            return False
        
        # Connect to MongoDB
        print(f"Connecting to MongoDB at: {Config.MONGO_URI}")
        client = MongoClient(Config.MONGO_URI)
        db = client.juris_ai
        collection = db.ipc_sections
        
        # Clear existing data
        collection.delete_many({})
        log_info("Cleared existing IPC sections from database")
        print("Cleared existing IPC sections from database")
        
        # Load dataset
        print(f"Loading dataset from: {dataset_path}")
        with open(dataset_path, 'r', encoding='utf-8') as f:
            sections = json.load(f)
        
        # Insert sections into MongoDB
        if sections:
            print(f"Inserting {len(sections)} sections into MongoDB")
            result = collection.insert_many(sections)
            log_info(f"Ingested {len(result.inserted_ids)} IPC sections into MongoDB")
            print(f"Ingested {len(result.inserted_ids)} IPC sections into MongoDB")
        else:
            log_error("No sections found in dataset")
            print("No sections found in dataset")
            return False
            
        # Create indexes
        collection.create_index("section_number", unique=True)
        collection.create_index("keywords")
        collection.create_index("synonyms")
        collection.create_index("vector_search_terms")
        collection.create_index("crime_category")
        collection.create_index("crime_subcategory")
        collection.create_index("severity_level")
        collection.create_index("crime_type_mapping")
        log_info("Created MongoDB indexes")
        print("Created MongoDB indexes")
        
        client.close()
        return True
        
    except Exception as e:
        log_error(f"Dataset ingestion failed: {str(e)}")
        print(f"Dataset ingestion failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = ingest_dataset_to_mongodb()
        if success:
            print("Dataset ingestion completed successfully")
            log_info("Dataset ingestion completed successfully")
        else:
            print("Dataset ingestion failed")
            log_error("Dataset ingestion failed")
            sys.exit(1)
    except Exception as e:
        print(f"Unexpected error during dataset ingestion: {e}")
        import traceback
        traceback.print_exc()
        log_error(f"Unexpected error during dataset ingestion: {e}")
        sys.exit(1)
