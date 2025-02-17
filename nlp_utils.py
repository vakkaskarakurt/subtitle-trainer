import nltk
import spacy
import streamlit as st
from difflib import SequenceMatcher
import re

@st.cache_resource(show_spinner="Dil modelleri yükleniyor...")
def load_nlp():
    """NLP modellerini yükle"""
    try:
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        return spacy.load('en_core_web_md')
    except OSError as e:
        st.error("""
        Dil modeli bulunamadı. Lütfen önce setup.py scriptini çalıştırın:
        ```
        python setup.py
        ```
        """)
        st.stop()

def analyze_answer(user_answer, correct_answer, nlp_model):
    """Detaylı cevap analizi"""
    if not user_answer or not correct_answer:
        return None
        
    def clean_text(text):
        text = re.sub(r'[^\w\s]', '', text)
        return ' '.join(text.lower().split())
    
    clean_user = clean_text(user_answer)
    clean_correct = clean_text(correct_answer)
    
    # Calculate similarities
    string_similarity = SequenceMatcher(None, clean_user, clean_correct).ratio()
    
    try:
        doc1 = nlp_model(user_answer.lower())
        doc2 = nlp_model(correct_answer.lower())
        semantic_similarity = doc1.similarity(doc2)
    except:
        semantic_similarity = 0
    
    # Detailed word analysis
    correct_words = re.findall(r'\b\w+\b', correct_answer.lower())
    user_words = re.findall(r'\b\w+\b', user_answer.lower())
    
    # Word order analysis
    correct_word_order = list(enumerate(correct_words))
    user_word_order = list(enumerate(user_words))
    
    # Find missing and extra words with positions
    missing_words = [(word, pos) for pos, word in correct_word_order 
                    if word not in user_words]
    extra_words = [(word, pos) for pos, word in user_word_order 
                   if word not in correct_words]
    
    # Calculate word order accuracy
    word_order_score = 0
    if user_words:
        common_words = set(correct_words) & set(user_words)
        if common_words:
            correct_positions = sum(1 for w in common_words 
                                 if correct_words.index(w) == user_words.index(w))
            word_order_score = correct_positions / len(common_words)
    
    return {
        'string_similarity': string_similarity,
        'semantic_similarity': semantic_similarity,
        'word_order_score': word_order_score,
        'missing_words': missing_words,
        'extra_words': extra_words,
        'total_words': len(correct_words),
        'correct_words': len(set(correct_words) & set(user_words))
    }