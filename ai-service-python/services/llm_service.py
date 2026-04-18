import requests
import json
import time
from utils.config import Config
from utils.logging import log_llm_call, log_error
from metrics.metrics_tracker import metrics_tracker

class LLMService:
    def __init__(self):
        self.model_provider = Config.MODEL_PROVIDER
        self.ollama_url = Config.OLLAMA_URL
        self.ollama_model = Config.OLLAMA_MODEL
        self.ollama_api_key = Config.OLLAMA_API_KEY
        self.openrouter_url = Config.OPENROUTER_URL
        self.openrouter_model = Config.OPENROUTER_MODEL
        self.openrouter_api_key = Config.OPENROUTER_API_KEY
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    def _call_ollama(self, prompt, max_tokens=None):
        """Call Ollama model directly"""
        try:
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False
            }
            
            if max_tokens:
                payload["options"] = {"num_predict": max_tokens}

            headers = {}
            if self.ollama_api_key:
                headers["Authorization"] = f"Bearer {self.ollama_api_key}"
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                headers=headers,
                timeout=120  # 2 minute timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                log_error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            log_error(f"Ollama call failed: {str(e)}")
            return None

    def _call_openrouter(self, prompt, max_tokens=None):
        if not self.openrouter_api_key:
            return None

        try:
            payload = {
                "model": self.openrouter_model,
                "messages": [
                    {"role": "system", "content": "You are an IPC-only legal assistant. Never cite non-IPC laws."},
                    {"role": "user", "content": prompt},
                ],
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens

            response = requests.post(
                self.openrouter_url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60,
            )
            if response.status_code == 200:
                result = response.json()
                choices = result.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content")

            log_error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            log_error(f"OpenRouter call failed: {str(e)}")
            return None
    
    def generate_response(self, prompt, max_tokens=None):
        """Generate response with retry logic and fallback"""
        for attempt in range(self.max_retries):
            try:
                log_llm_call(prompt)
                
                if self.model_provider == "OLLAMA_LOCAL":
                    response = self._call_ollama(prompt, max_tokens)
                else:
                    response = None

                if not response:
                    response = self._call_openrouter(prompt, max_tokens)

                if response:
                    log_llm_call(prompt, response)
                    metrics_tracker.record_llm_call(success=True)
                    return response
                        
                # If we reach here, the primary method failed
                log_error(f"LLM call attempt {attempt + 1} failed")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    
            except Exception as e:
                log_error(f"LLM call exception on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
        
        # All retries failed
        log_error("All LLM call retries failed")
        metrics_tracker.record_llm_call(success=False)
        return "AI reasoning service temporarily unavailable."

# Global LLM service instance
llm_service = LLMService()
