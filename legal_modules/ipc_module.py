import json
import os
from utils.config import Config
from utils.logging import log_info, log_error

class IPCModule:
    def __init__(self):
        self.dataset_path = Config.LEGAL_ACTS["IPC"]["dataset"]
        self.sections = []
        self.section_index = {}  # For quick lookup by section number
        self.load_dataset()
    
    def load_dataset(self):
        """Load IPC dataset from JSON file"""
        try:
            # Handle path differently when running from ai-service-python directory
            if os.getcwd().endswith("ai-service-python"):
                dataset_full_path = os.path.join("..", self.dataset_path)
            else:
                dataset_full_path = os.path.join(os.getcwd(), self.dataset_path)
                
            print(f"Loading dataset from: {dataset_full_path}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Dataset path in config: {self.dataset_path}")
            
            # Check if file exists
            if not os.path.exists(dataset_full_path):
                # Try alternative path (relative to project root)
                alt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), self.dataset_path)
                print(f"Trying alternative path: {alt_path}")
                if os.path.exists(alt_path):
                    dataset_full_path = alt_path
                else:
                    # Try absolute path
                    abs_path = os.path.join("D:", "anthropic", "JurisAI", self.dataset_path)
                    print(f"Trying absolute path: {abs_path}")
                    if os.path.exists(abs_path):
                        dataset_full_path = abs_path
                    else:
                        raise FileNotFoundError(f"Dataset file not found at {dataset_full_path} or {alt_path} or {abs_path}")
            
            with open(dataset_full_path, 'r', encoding='utf-8') as f:
                self.sections = json.load(f)
            
            # Create index for quick lookup
            for section in self.sections:
                self.section_index[section["section_number"]] = section
                
            log_info(f"Loaded {len(self.sections)} IPC sections from {dataset_full_path}")
        except Exception as e:
            log_error(f"Failed to load IPC dataset: {str(e)}")
            raise
    
    def get_section(self, section_number):
        """Get a specific IPC section by number"""
        return self.section_index.get(str(section_number), None)
    
    def get_all_sections(self):
        """Get all IPC sections"""
        return self.sections
    
    def search_sections(self, query):
        """Search for sections matching a query term"""
        results = []
        query_lower = query.lower()
        
        for section in self.sections:
            # Search in title, description, and keywords
            if (query_lower in section["title"].lower() or 
                query_lower in section["description"].lower() or
                any(query_lower in keyword.lower() for keyword in section["keywords"]) or
                any(query_lower in term.lower() for term in section["vector_search_terms"])):
                results.append(section)
        
        return results
    
    def get_related_sections(self, section_number):
        """Get related sections for a given section number"""
        section = self.get_section(section_number)
        if not section:
            return []
        
        related = []
        for related_section_num in section["related_sections"]:
            related_section = self.get_section(related_section_num)
            if related_section:
                related.append(related_section)
        
        return related
    
    def get_crime_type_mapping(self, section_number):
        """Get crime type mapping for a section"""
        section = self.get_section(section_number)
        if not section:
            return None
        
        return section.get("crime_type_mapping", {})

# Global IPC module instance
ipc_module = IPCModule()