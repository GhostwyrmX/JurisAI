import time
import json
import os
from utils.logging import log_info, log_error

class MetricsTracker:
    def __init__(self):
        self.metrics = {
            "startup_time": 0,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0,
            "total_llm_calls": 0,
            "successful_llm_calls": 0,
            "failed_llm_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_vector_searches": 0,
            "start_time": time.time()
        }
        self.request_times = []
        
    def record_startup(self, duration):
        """Record application startup time"""
        self.metrics["startup_time"] = duration
        log_info(f"Application started in {duration:.2f} seconds")
        
    def record_request(self, duration, success=True):
        """Record API request metrics"""
        self.metrics["total_requests"] += 1
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
            
        self.request_times.append(duration)
        self.metrics["avg_response_time"] = sum(self.request_times) / len(self.request_times)
        
    def record_llm_call(self, success=True):
        """Record LLM call metrics"""
        self.metrics["total_llm_calls"] += 1
        if success:
            self.metrics["successful_llm_calls"] += 1
        else:
            self.metrics["failed_llm_calls"] += 1
            
    def record_cache_hit(self):
        """Record cache hit"""
        self.metrics["cache_hits"] += 1
        
    def record_cache_miss(self):
        """Record cache miss"""
        self.metrics["cache_misses"] += 1
        
    def record_vector_search(self):
        """Record vector search"""
        self.metrics["total_vector_searches"] += 1
        
    def get_metrics(self):
        """Get current metrics"""
        # Calculate uptime
        self.metrics["uptime"] = time.time() - self.metrics["start_time"]
        return self.metrics
        
    def save_metrics(self, filepath="metrics/metrics.json"):
        """Save metrics to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save metrics
            with open(filepath, 'w') as f:
                json.dump(self.metrics, f, indent=2)
                
            log_info(f"Metrics saved to {filepath}")
        except Exception as e:
            log_error(f"Failed to save metrics: {str(e)}")

# Global metrics tracker instance
metrics_tracker = MetricsTracker()