import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging
def setup_logger(name, log_file, level=logging.INFO):
    """Function to setup as many loggers as you want"""
    
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

# Create different loggers for different purposes
app_logger = setup_logger('app', 'logs/app.log')
error_logger = setup_logger('error', 'logs/error.log')
query_logger = setup_logger('query', 'logs/query.log')

def log_startup():
    app_logger.info("JURIS AI system starting up")

def log_dataset_validation(status, details=""):
    app_logger.info(f"Dataset validation: {status}. {details}")

def log_user_query(query, user_id=None):
    query_logger.info(f"User query: {query}" + (f" by user: {user_id}" if user_id else ""))

def log_llm_call(prompt, response="", error=""):
    if error:
        error_logger.error(f"LLM call error: {error}")
    else:
        app_logger.info(f"LLM call - Prompt: {prompt[:100]}... Response: {response[:100]}...")

def log_error(error_msg):
    error_logger.error(error_msg)

def log_info(info_msg):
    app_logger.info(info_msg)