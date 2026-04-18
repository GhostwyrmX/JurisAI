import os
import base64
from gtts import gTTS
from utils.logging import log_info, log_error
from cache.redis_cache import cache

class TTSService:
    def __init__(self):
        self.is_available = True
        log_info("TTS service initialized with gTTS")
        
        # Create audio directory if it doesn't exist
        self.audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audio")
        os.makedirs(self.audio_dir, exist_ok=True)
        
    def synthesize_speech(self, text, language="english"):
        """Convert text to speech and return base64 encoded audio"""
        try:
            # Check cache first
            cache_key = f"tts_{hash(text)}_{language}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Map language codes
            lang_map = {
                "english": "en",
                "hindi": "hi",
                "marathi": "mr",
                "tamil": "ta",
                "bengali": "bn"
            }
            
            tts_lang = lang_map.get(language, "en")
            
            # Generate unique filename
            filename = f"tts_output_{hash(text)}.mp3"
            audio_path = os.path.join(self.audio_dir, filename)
            
            # Generate speech
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            tts.save(audio_path)
            
            # Read file and encode as base64
            with open(audio_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                base64_audio = base64.b64encode(audio_data).decode('utf-8')
            
            # Return data URL
            data_url = f"data:audio/mp3;base64,{base64_audio}"
            
            # Cache result
            cache.set(cache_key, data_url, ttl=86400)  # 24 hours
            
            # Clean up file (optional, since it's cached)
            try:
                os.remove(audio_path)
            except:
                pass
            
            return data_url
            
        except Exception as e:
            log_error(f"TTS synthesis failed: {str(e)}")
            return None
    
    def is_tts_available(self):
        """Check if TTS service is available"""
        return self.is_available

# Global TTS service instance
tts_service = TTSService()