import json
import hashlib
import os
from utils.logging import log_dataset_validation, log_error

def validate_json_syntax(file_path):
    """Validate JSON syntax of the dataset file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        log_dataset_validation("PASS", "JSON syntax is valid")
        print("JSON syntax is valid")
        return True, data
    except json.JSONDecodeError as e:
        log_dataset_validation("FAIL", f"JSON syntax error: {str(e)}")
        print(f"JSON syntax error: {str(e)}")
        return False, None
    except Exception as e:
        log_dataset_validation("FAIL", f"Error reading file: {str(e)}")
        print(f"Error reading file: {str(e)}")
        return False, None

def validate_ipc_sections(data):
    """Validate IPC sections for required fields and data integrity"""
    if not isinstance(data, list):
        log_dataset_validation("FAIL", "Dataset should be a list of IPC sections")
        print("Dataset should be a list of IPC sections")
        return False
    
    required_fields = [
        "section_number", "title", "chapter", "description",
        "section_text", "crime_category", "crime_subcategory",
        "severity_level", "legal_elements", "keywords", "synonyms",
        "punishment", "example_scenarios", "scenario_training",
        "related_sections", "crime_type_mapping", "court_judgment_links",
        "vector_search_terms", "citation"
    ]
    
    section_numbers = set()
    
    for i, section in enumerate(data):
        # Check for duplicate section numbers
        if section.get("section_number") in section_numbers:
            log_dataset_validation("FAIL", f"Duplicate section number found: {section.get('section_number')} at index {i}")
            print(f"Duplicate section number found: {section.get('section_number')} at index {i}")
            return False
        section_numbers.add(section.get("section_number"))
        
        # Check for missing fields
        for field in required_fields:
            if field not in section:
                log_dataset_validation("FAIL", f"Missing field '{field}' in section {section.get('section_number', 'unknown')} at index {i}")
                print(f"Missing field '{field}' in section {section.get('section_number', 'unknown')} at index {i}")
                return False
                
        # Check data types
        if not isinstance(section.get("legal_elements"), list):
            log_dataset_validation("FAIL", f"Invalid data type for 'legal_elements' in section {section.get('section_number', 'unknown')}")
            print(f"Invalid data type for 'legal_elements' in section {section.get('section_number', 'unknown')}")
            return False
            
        if not isinstance(section.get("keywords"), list):
            log_dataset_validation("FAIL", f"Invalid data type for 'keywords' in section {section.get('section_number', 'unknown')}")
            print(f"Invalid data type for 'keywords' in section {section.get('section_number', 'unknown')}")
            return False

        if not isinstance(section.get("synonyms"), list):
            log_dataset_validation("FAIL", f"Invalid data type for 'synonyms' in section {section.get('section_number', 'unknown')}")
            print(f"Invalid data type for 'synonyms' in section {section.get('section_number', 'unknown')}")
            return False
            
        if not isinstance(section.get("example_scenarios"), list):
            log_dataset_validation("FAIL", f"Invalid data type for 'example_scenarios' in section {section.get('section_number', 'unknown')}")
            print(f"Invalid data type for 'example_scenarios' in section {section.get('section_number', 'unknown')}")
            return False

        if not isinstance(section.get("scenario_training"), list):
            log_dataset_validation("FAIL", f"Invalid data type for 'scenario_training' in section {section.get('section_number', 'unknown')}")
            print(f"Invalid data type for 'scenario_training' in section {section.get('section_number', 'unknown')}")
            return False
            
        if not isinstance(section.get("related_sections"), list):
            log_dataset_validation("FAIL", f"Invalid data type for 'related_sections' in section {section.get('section_number', 'unknown')}")
            print(f"Invalid data type for 'related_sections' in section {section.get('section_number', 'unknown')}")
            return False

        if not isinstance(section.get("court_judgment_links"), list):
            log_dataset_validation("FAIL", f"Invalid data type for 'court_judgment_links' in section {section.get('section_number', 'unknown')}")
            print(f"Invalid data type for 'court_judgment_links' in section {section.get('section_number', 'unknown')}")
            return False
            
        if not isinstance(section.get("vector_search_terms"), list):
            log_dataset_validation("FAIL", f"Invalid data type for 'vector_search_terms' in section {section.get('section_number', 'unknown')}")
            print(f"Invalid data type for 'vector_search_terms' in section {section.get('section_number', 'unknown')}")
            return False

        if not isinstance(section.get("crime_type_mapping"), dict):
            log_dataset_validation("FAIL", f"Invalid data type for 'crime_type_mapping' in section {section.get('section_number', 'unknown')}")
            print(f"Invalid data type for 'crime_type_mapping' in section {section.get('section_number', 'unknown')}")
            return False

        if not isinstance(section.get("citation"), dict):
            log_dataset_validation("FAIL", f"Invalid data type for 'citation' in section {section.get('section_number', 'unknown')}")
            print(f"Invalid data type for 'citation' in section {section.get('section_number', 'unknown')}")
            return False
    
    log_dataset_validation("PASS", f"All {len(data)} sections validated successfully")
    print(f"All {len(data)} sections validated successfully")
    return True

def calculate_dataset_hash(file_path):
    """Calculate SHA256 hash of the dataset file for versioning"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def validate_dataset(file_path):
    """Main validation function that runs all validations"""
    log_dataset_validation("START", f"Validating dataset: {file_path}")
    print(f"Starting validation of dataset: {file_path}")
    
    # Validate JSON syntax
    print("Validating JSON syntax...")
    is_valid, data = validate_json_syntax(file_path)
    if not is_valid:
        print("JSON syntax validation failed")
        return False
    print("JSON syntax validation passed")
    
    # Validate IPC sections
    print("Validating IPC sections...")
    is_valid = validate_ipc_sections(data)
    if not is_valid:
        print("IPC sections validation failed")
        return False
    print("IPC sections validation passed")
    
    # Calculate dataset hash
    dataset_hash = calculate_dataset_hash(file_path)
    log_dataset_validation("COMPLETE", f"Dataset hash: {dataset_hash}")
    print(f"Dataset validation completed successfully. Hash: {dataset_hash}")
    
    return True
