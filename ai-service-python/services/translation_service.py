from utils.logging import log_info, log_error
from cache.redis_cache import cache
import requests
import json
try:
    from googletrans import Translator
    GOOGLE_TRANS_AVAILABLE = True
except ImportError:
    GOOGLE_TRANS_AVAILABLE = False
    log_error("googletrans not available, using fallback translation")

class TranslationService:
    def __init__(self):
        # Supported languages mapping
        self.supported_languages = {
            "english": "en",
            "hindi": "hi",
            "marathi": "mr",
            "tamil": "ta",
            "bengali": "bn"
        }
        
        # Initialize Google Translate
        self.translator = None
        if GOOGLE_TRANS_AVAILABLE:
            try:
                self.translator = Translator()
                log_info("Google Translate initialized")
            except Exception as e:
                log_error(f"Failed to initialize Google Translate: {str(e)}")
        
        # Basic legal term translations (for enhancement)
        self.legal_terms = {
            "hindi": {
                "section": "धारा",
                "punishment": "सजा",
                "imprisonment": "कारावास",
                "fine": "जुर्माना",
                "police": "पुलिस",
                "court": "अदालत",
                "lawyer": "वकील",
                "crime": "अपराध",
                "arrest": "गिरफ्तारी",
                "bail": "जमानत",
                "warrant": "वारंट",
                "evidence": "सबूत",
                "witness": "गवाह",
                "complaint": "शिकायत",
                "investigation": "जांच",
                "trial": "मुकदमा",
                "sentence": "सजा",
                "appeal": "अपील",
                "conviction": "दोषसिद्धि",
                "acquittal": "बरी",
                "murder": "हत्या",
                "theft": "चोरी",
                "assault": "हमला",
                "rape": "बलात्कार",
                "fraud": "धोखा",
                "robbery": "डकैती"
            },
            "marathi": {
                "section": "कलम",
                "punishment": "शिक्षा",
                "imprisonment": "तुरुंगवास",
                "fine": "दंड",
                "police": "पोलीस",
                "court": "न्यायालय",
                "lawyer": "वकील",
                "crime": "गुन्हा",
                "arrest": "अटक",
                "bail": "जामीन",
                "warrant": "वॉरंट",
                "evidence": "पुरावा",
                "witness": "साक्षी",
                "complaint": "तक्रार",
                "investigation": "तपास",
                "trial": "खटला",
                "sentence": "शिक्षा",
                "appeal": "अपील",
                "conviction": "दोषारोप",
                "acquittal": "मुक्तता",
                "murder": "खून",
                "theft": "चोरी",
                "assault": "हल्ला",
                "rape": "बलात्कार",
                "fraud": "फसवणूक",
                "robbery": "डकैती"
            },
            "tamil": {
                "section": "பிரிவு",
                "punishment": "தண்டனை",
                "imprisonment": "சிறைத்தண்டனை",
                "fine": "அபராதம்",
                "police": "காவல்துறை",
                "court": "நீதிமன்றம்",
                "lawyer": "வழக்கறிஞர்",
                "crime": "குற்றம்",
                "arrest": "கைது",
                "bail": "பிணை",
                "warrant": "வாரண்ட்",
                "evidence": "ஆதாரம்",
                "witness": "சாட்சி",
                "complaint": "புகார்",
                "investigation": "விசாரணை",
                "trial": "வழக்கு",
                "sentence": "தண்டனை",
                "appeal": "மேல்முறையீடு",
                "conviction": "குற்றவியல்",
                "acquittal": "விடுவிப்பு",
                "murder": "கொலை",
                "theft": "திருட்டு",
                "assault": "தாக்குதல்",
                "rape": "பாலியல் வன்முறை",
                "fraud": "ஏமாற்றம்",
                "robbery": "கொள்ளை"
            },
            "bengali": {
                "section": "ধারা",
                "punishment": "শাস্তি",
                "imprisonment": "কারাদণ্ড",
                "fine": "জরিমানা",
                "police": "পুলিশ",
                "court": "আদালত",
                "lawyer": "উকিল",
                "crime": "অপরাধ",
                "arrest": "গ্রেপ্তার",
                "bail": "জামিন",
                "warrant": "ওয়ারেন্ট",
                "evidence": "প্রমাণ",
                "witness": "সাক্ষী",
                "complaint": "অভিযোগ",
                "investigation": "তদন্ত",
                "trial": "মামলা",
                "sentence": "শাস্তি",
                "appeal": "আপিল",
                "conviction": "দোষী সাব্যস্ত",
                "acquittal": "খালাস",
                "murder": "খুন",
                "theft": "চুরি",
                "assault": "আক্রমণ",
                "rape": "ধর্ষণ",
                "fraud": "প্রতারণা",
                "robbery": "ডাকাতি"
            }
        }
        
    def _load_models(self):
        """Load translation models for supported language pairs"""
        try:
            # For now, we'll skip loading models and use a simpler approach
            # The Helsinki-NLP models are large and may not be available
            log_info("Translation models loading skipped - using fallback translation")
            self.models = {}  # Empty dict to force fallback
            
        except Exception as e:
            log_error(f"Failed to initialize translation models: {str(e)}")
        
    def detect_language(self, text):
        """Detect the language of the input text"""
        # Simple heuristic-based detection for now
        # In production, use a proper language detection library
        text_lower = text.lower()
        
        # Check for Devanagari script (Hindi, Marathi)
        if any(ord(char) in range(0x0900, 0x097F) for char in text):
            return "hindi"  # Could be Hindi or Marathi, default to Hindi
            
        # Check for Tamil script
        if any(ord(char) in range(0x0B80, 0x0BFF) for char in text):
            return "tamil"
            
        # Check for Bengali script
        if any(ord(char) in range(0x0980, 0x09FF) for char in text):
            return "bengali"
            
        return "english"  # Default
    
    def translate(self, text, target_language):
        """Translate text to target language"""
        try:
            # Check cache first
            cache_key = f"translation_{hash(text)}_{target_language}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Validate target language
            if target_language not in self.supported_languages:
                log_error(f"Unsupported language: {target_language}")
                return None
            
            # If target is English, return original text
            if target_language == "english":
                return text
            
            # Try full translation first
            translated_text = self._translate_full_text(text, target_language)
            
            # If full translation failed, enhance with legal terms
            if translated_text == text:
                translated_text = self._enhance_with_legal_terms(text, target_language)
            
            # If still no translation, provide a fallback
            if not translated_text or translated_text == text:
                translated_text = f"[{target_language.upper()}] {text}"
            
            # Cache result
            cache.set(cache_key, translated_text, ttl=86400)  # 24 hours
            
            log_info(f"Translated text to {target_language}")
            return translated_text
            
        except Exception as e:
            log_error(f"Translation failed: {str(e)}")
            return f"[{target_language.upper()}] {text}"
    
    def _translate_full_text(self, text, target_language):
        """Translate full text using Google Translate"""
        if not self.translator:
            return text
            
        try:
            target_code = self.supported_languages[target_language]
            result = self.translator.translate(text, dest=target_code, src='en')
            return result.text
        except Exception as e:
            log_error(f"Google Translate failed: {str(e)}")
            return text
    
    def _enhance_with_legal_terms(self, text, target_language):
        """Enhance translation with legal terms dictionary"""
        if target_language not in self.legal_terms:
            return text
            
        terms = self.legal_terms[target_language]
        translated_text = text
        
        # Replace legal terms (case-insensitive)
        for english_term, translated_term in terms.items():
            # Replace whole words only
            import re
            pattern = r'\b' + re.escape(english_term) + r'\b'
            translated_text = re.sub(pattern, translated_term, translated_text, flags=re.IGNORECASE)
        
        return translated_text

# Global translation service instance
translation_service = TranslationService()