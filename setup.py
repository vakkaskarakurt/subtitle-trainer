import nltk
import spacy

def setup_nlp_resources():
    """
    İlk kurulum için gerekli NLTK ve spaCy kaynaklarını indirir.
    Bu script sadece bir kere çalıştırılmalıdır.
    """
    print("NLTK kaynakları indiriliyor...")
    nltk.download('punkt')
    
    print("\nspaCy modeli indiriliyor...")
    try:
        spacy.load('en_core_web_md')
        print("spaCy modeli zaten yüklü.")
    except OSError:
        import os
        os.system('python -m spacy download en_core_web_md')
        print("spaCy modeli indirildi.")

if __name__ == "__main__":
    setup_nlp_resources()