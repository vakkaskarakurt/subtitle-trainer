import streamlit as st
from datetime import datetime
from translation_manager import TranslationManager

def initialize_session_state():
    """Oturum durumunu başlat"""
    if 'initialized' not in st.session_state:
        st.session_state.update({
            'initialized': True,
            'sentence_data': [],
            'current_index': 0,
            'translations': {},
            'show_answer': False,
            'total_duration': 0,
            'translation_manager': TranslationManager(),
            'statistics': {
                'correct_answers': 0,
                'total_attempts': 0,
                'average_similarity': []
            }
        })

def save_progress(sentence_data, current_index, translations):
    """İlerlemeyi kaydet"""
    st.session_state.progress_data = {
        'timestamp': datetime.now().isoformat(),
        'current_index': current_index,
        'total_sentences': len(sentence_data),
        'translations': translations
    }

def load_progress():
    """Kaydedilmiş ilerlemeyi yükle"""
    return st.session_state.get('progress_data', None)

def update_state(key, value):
    """Session state'i güncelle"""
    if key in st.session_state:
        st.session_state[key] = value

def get_state(key, default=None):
    """Session state'ten değer al"""
    return st.session_state.get(key, default)

def clear_state():
    """Session state'i temizle"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session_state()