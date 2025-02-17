from googletrans import Translator
import time

class TranslationManager:
    def __init__(self):
        self.translator = Translator()
        self.cache = {}
        self.retries = 3
        self.delay = 1  # seconds
    
    def translate(self, text):
        if text in self.cache:
            return self.cache[text]
            
        for attempt in range(self.retries):
            try:
                translation = self.translator.translate(text, dest='tr', src='en').text
                if translation:
                    self.cache[text] = translation
                    return translation
            except Exception as e:
                if attempt == self.retries - 1:
                    return f"Çeviri hatası: {str(e)}"
                time.sleep(self.delay)
        
        return "Çeviri yapılamadı."