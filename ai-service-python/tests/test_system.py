import unittest
import sys
import os
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validation import validate_dataset
from utils.config import Config

class TestJURISAI(unittest.TestCase):
    
    def test_dataset_validation(self):
        """Test that the IPC dataset validates correctly"""
        dataset_path = os.path.join(os.getcwd(), Config.LEGAL_ACTS["IPC"]["dataset"])
        
        # Check that dataset file exists
        self.assertTrue(os.path.exists(dataset_path), "IPC dataset file not found")
        
        # Validate dataset
        is_valid = validate_dataset(dataset_path)
        self.assertTrue(is_valid, "IPC dataset validation failed")
    
    def test_config_loading(self):
        """Test that configuration loads correctly"""
        # Check that required config values are present
        self.assertIsNotNone(Config.MONGO_URI, "MONGO_URI not set")
        self.assertIsNotNone(Config.JWT_SECRET, "JWT_SECRET not set")
        self.assertIsNotNone(Config.MODEL_PROVIDER, "MODEL_PROVIDER not set")
        self.assertIsNotNone(Config.OLLAMA_URL, "OLLAMA_URL not set")
        self.assertIsNotNone(Config.REDIS_URL, "REDIS_URL not set")
        self.assertIsNotNone(Config.EMBEDDING_MODEL, "EMBEDDING_MODEL not set")
        self.assertIsNotNone(Config.VECTOR_INDEX_PATH, "VECTOR_INDEX_PATH not set")
        
        # Check that legal acts registry is properly configured
        self.assertIn("IPC", Config.LEGAL_ACTS, "IPC not found in LEGAL_ACTS")
        self.assertIn("dataset", Config.LEGAL_ACTS["IPC"], "dataset path not found in IPC config")
        self.assertIn("vector_index", Config.LEGAL_ACTS["IPC"], "vector_index path not found in IPC config")

if __name__ == '__main__':
    unittest.main()