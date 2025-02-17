import streamlit as st
import pysrt
from difflib import SequenceMatcher
import nltk
import re
import spacy
from googletrans import Translator
from pathlib import Path
import time
import io
import chardet
import json
from datetime import datetime
from streamlit_shortcuts import add_keyboard_shortcuts, button

# Custom styles and configurations
st.set_page_config(
    page_title="İngilizce Altyazı Öğrenme Programı",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #1E1E1E;
        color: white;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #2A2A2A;
        color: white;
        font-size: 1.1rem;
        padding: 15px;
        border-radius: 8px;
    }
    .stProgress > div > div > div {
        background-color: #2196F3;
    }
    .success-text {
        color: #4CAF50;
        font-weight: bold;
    }
    .error-text {
        color: #f44336;
        font-weight: bold;
    }
    .info-box {
        background-color: #2A2A2A;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #3A3A3A;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize NLTK and spaCy
@st.cache_resource(show_spinner="Dil modelleri yükleniyor...")
def load_nlp():
    """NLP modellerini yükle"""
    try:
        # NLTK kontrolleri
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        # spaCy modelini yükle
        return spacy.load('en_core_web_md')
    except OSError as e:
        st.error("""
        Dil modeli bulunamadı. Lütfen önce setup.py scriptini çalıştırın:
        ```
        python setup.py
        ```
        """)
        st.stop()

nlp = load_nlp()

def get_time_in_seconds(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

def format_seconds_to_time(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def detect_encoding(file_content):
    """Detect the encoding of the file content"""
    result = chardet.detect(file_content)
    return result['encoding']

def read_srt_file(file_content):
    """Try different encodings to read the srt file"""
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1', 'iso-8859-9', 
                'cp1252', 'cp1254', 'ascii', 'utf-16', 'utf-32']
    
    # First try detected encoding
    detected_encoding = detect_encoding(file_content)
    if detected_encoding:
        encodings.insert(0, detected_encoding)
    
    for encoding in encodings:
        try:
            content = file_content.decode(encoding)
            if content.startswith('\ufeff'):
                content = content[1:]
            content = ''.join(char for char in content if ord(char) < 65536)
            return pysrt.from_string(content)
        except:
            continue
    
    raise ValueError("Hiçbir karakter kodlaması ile dosya okunamadı.")

def process_subtitles(subs):
    """Parse subtitles into sentences with detailed metadata"""
    combined_text = ""
    current_sentence_start = None
    temp_subtitle_data = []
    
    for sub in subs:
        text = sub.text.strip()
        # Enhanced text cleaning
        text = re.sub(r'\([^)]*\)', '', text)  # Remove parentheses and content
        text = re.sub(r'^[A-Z]+:', '', text)   # Remove speaker labels
        text = re.sub(r'</?\w+>', '', text)    # Remove HTML-like tags
        text = re.sub(r'\s+', ' ', text)       # Normalize whitespace
        text = text.strip()
        
        if not text:
            continue
            
        if current_sentence_start is None:
            current_sentence_start = {
                'start': str(sub.start).split(',')[0],
                'start_seconds': get_time_in_seconds(str(sub.start).split(',')[0]),
                'original_text': text
            }
        else:
            current_sentence_start['original_text'] += f" {text}"
            
        combined_text += " " + text
        
        if text.rstrip()[-1] in '.!?':
            temp_subtitle_data.append({
                'text': combined_text.strip(),
                'start': current_sentence_start['start'],
                'end': str(sub.end).split(',')[0],
                'start_seconds': current_sentence_start['start_seconds'],
                'end_seconds': get_time_in_seconds(str(sub.end).split(',')[0]),
                'original_text': current_sentence_start['original_text']
            })
            combined_text = ""
            current_sentence_start = None

    # Process into proper sentences
    sentence_data = []
    for sub in temp_subtitle_data:
        sentences = nltk.sent_tokenize(sub['text'])
        for sentence in sentences:
            if sentence.strip():
                sentence_data.append({
                    'text': sentence.strip(),
                    'start': sub['start'],
                    'end': sub['end'],
                    'start_seconds': sub['start_seconds'],
                    'end_seconds': sub['end_seconds'],
                    'original_text': sub['original_text'],
                    'word_count': len(re.findall(r'\b\w+\b', sentence))
                })
    
    return sentence_data

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

def analyze_answer(user_answer, correct_answer, nlp_model):
    """Detailed answer analysis with multiple metrics"""
    if not user_answer or not correct_answer:
        return None
        
    # Text cleaning
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

def save_progress(sentence_data, current_index, translations):
    """Save current progress to session state"""
    st.session_state.progress_data = {
        'timestamp': datetime.now().isoformat(),
        'current_index': current_index,
        'total_sentences': len(sentence_data),
        'translations': translations
    }
    
def load_progress():
    """Load saved progress from session state"""
    return st.session_state.get('progress_data', None)

def main():
    # Initialize session state
    if 'update_required' in st.session_state and st.session_state.update_required:
        st.session_state.update_required = False
        st.rerun()
        
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

    # Navigation functions
    def go_to_next():
        if st.session_state.sentence_data and st.session_state.current_index < len(st.session_state.sentence_data) - 1:
            st.session_state.current_index += 1
            st.session_state.show_answer = False
            st.session_state.update_required = True

    def go_to_previous():
        if st.session_state.sentence_data and st.session_state.current_index > 0:
            st.session_state.current_index -= 1
            st.session_state.show_answer = False
            st.session_state.update_required = True

    def toggle_answer():
        if st.session_state.sentence_data:
            st.session_state.show_answer = not st.session_state.show_answer
            st.session_state.update_required = True

    def check_answer():
        if st.session_state.sentence_data and 'answer_input' in st.session_state:
            user_answer = st.session_state.answer_input
            current = st.session_state.sentence_data[st.session_state.current_index]
            
            st.session_state.statistics['total_attempts'] += 1
            analysis = analyze_answer(user_answer, current['text'], nlp)
            
            if analysis:
                st.session_state.statistics['average_similarity'].append(analysis['string_similarity'])
                
                if analysis['string_similarity'] == 1.0:
                    st.session_state.statistics['correct_answers'] += 1
                    st.success(f"""
                    ✅ Mükemmel!
                    - String Benzerliği: {analysis['string_similarity']:.1%}
                    - Anlamsal Benzerlik: {analysis['semantic_similarity']:.1%}
                    - Kelime Sırası Doğruluğu: {analysis['word_order_score']:.1%}
                    """)
                    
                    time.sleep(1)
                    if st.session_state.current_index < len(st.session_state.sentence_data) - 1:
                        st.session_state.current_index += 1
                        st.session_state.show_answer = False
                        st.session_state.update_required = True
                else:
                    st.error(f"""
                    ❌ Tekrar deneyin
                    - String Benzerliği: {analysis['string_similarity']:.1%}
                    - Anlamsal Benzerlik: {analysis['semantic_similarity']:.1%}
                    - Kelime Sırası Doğruluğu: {analysis['word_order_score']:.1%}
                    """)
                    
                    # Detailed word analysis
                    with st.expander("🔍 Detaylı Kelime Analizi"):
                        if analysis['missing_words']:
                            st.warning("❌ Eksik kelimeler:")
                            for word, pos in analysis['missing_words']:
                                st.markdown(f"- {word} (pozisyon: {pos + 1})")
                        
                        if analysis['extra_words']:
                            st.warning("⚠️ Fazladan kullanılan kelimeler:")
                            for word, pos in analysis['extra_words']:
                                st.markdown(f"- {word} (pozisyon: {pos + 1})")
                        
                        st.info(f"""
                        📊 İstatistikler:
                        - Toplam kelime sayısı: {analysis['total_words']}
                        - Doğru kelime sayısı: {analysis['correct_words']}
                        - Doğruluk oranı: {analysis['correct_words']/analysis['total_words']:.1%}
                        """)

    # Add keyboard shortcuts with modified key combinations
    add_keyboard_shortcuts({
        'ArrowRight': go_to_next,
        'ArrowLeft': go_to_previous,
        'ctrl+Space': toggle_answer,  # Space tuşu yerine Ctrl+Space kullanıyoruz
        'ctrl+Enter': check_answer    # Enter tuşu yerine Ctrl+Enter kullanıyoruz
    })

    # Sidebar
    with st.sidebar:
        st.title("📚 Kontroller")
        uploaded_file = st.file_uploader("Altyazı Dosyası Seç (.srt)", type=['srt'])
        
        if uploaded_file:
            file_content = uploaded_file.read()
            if 'last_file' not in st.session_state or st.session_state.last_file != uploaded_file.name:
                try:
                    subs = read_srt_file(file_content)
                    with st.spinner("Altyazılar işleniyor..."):
                        st.session_state.sentence_data = process_subtitles(subs)
                        st.session_state.total_duration = st.session_state.sentence_data[-1]['end_seconds']
                        st.session_state.current_index = 0
                        st.session_state.show_answer = False
                        st.session_state.last_file = uploaded_file.name
                except Exception as e:
                    st.error(f"Dosya yüklenirken hata oluştu: {str(e)}")
        
        # Statistics in sidebar
        if st.session_state.sentence_data:
            st.subheader("📊 İstatistikler")
            stats = st.session_state.statistics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Doğru Cevaplar", stats['correct_answers'])
            with col2:
                st.metric("Toplam Deneme", stats['total_attempts'])
            
            if stats['average_similarity']:
                avg_sim = sum(stats['average_similarity']) / len(stats['average_similarity'])
                st.progress(avg_sim, "Ortalama Benzerlik")
        
        # Navigation controls with shortcuts
        st.subheader("🎯 Navigasyon")
        col1, col2, col3 = st.columns(3)
        with col1:
            button("◀ Önceki", "ArrowLeft", 
                  go_to_previous,
                  disabled=not st.session_state.sentence_data or st.session_state.current_index <= 0,
                  hint=True)
        
        with col2:
            if st.session_state.sentence_data:
                jump_to = st.number_input("Altyazı No", 
                    min_value=1, 
                    max_value=len(st.session_state.sentence_data),
                    value=st.session_state.current_index + 1)
                if jump_to != st.session_state.current_index + 1:
                    st.session_state.current_index = jump_to - 1
                    st.session_state.show_answer = False

        with col3:
            button("Sonraki ▶", "ArrowRight",
                  go_to_next,
                  disabled=not st.session_state.sentence_data or 
                  st.session_state.current_index >= len(st.session_state.sentence_data) - 1,
                  hint=True)

    # Main content area
    if st.session_state.sentence_data:
        current = st.session_state.sentence_data[st.session_state.current_index]
        
        # Progress bars
        col1, col2 = st.columns(2)
        with col1:
            progress = (st.session_state.current_index + 1) / len(st.session_state.sentence_data)
            st.progress(progress, "Genel İlerleme")
            st.caption(f"İlerleme: {st.session_state.current_index + 1}/{len(st.session_state.sentence_data)}")
        
        with col2:
            time_progress = current['start_seconds'] / st.session_state.total_duration
            st.progress(time_progress, "Zaman İlerlemesi")
            st.caption(f"⏱️ {current['start']} → {format_seconds_to_time(st.session_state.total_duration)}")
        
        # Translation section
        st.subheader("🌍 Türkçe Metin")
        if current['text'] not in st.session_state.translations:
            with st.spinner("Çeviri yapılıyor..."):
                st.session_state.translations[current['text']] = st.session_state.translation_manager.translate(current['text'])
        
        st.markdown(f"""
        <div class="info-box">
            <p style='font-size: 1.2rem; text-align: center;'>
                {st.session_state.translations[current['text']]}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Answer section with shortcuts
        st.subheader("✍️ İngilizce cümleyi yazın")
        user_answer = st.text_area(
            "",
            key="answer_input",
            height=100,
            placeholder="Cevabınızı buraya yazın..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            button("✓ Kontrol Et", "ctrl+Enter", check_answer, hint=True)
        
        with col2:
            button("👁 Cevabı Göster/Gizle", "ctrl+Space", toggle_answer, hint=True)
        
        if st.session_state.show_answer:
            st.markdown(f"""
            <div class="info-box" style="background-color: #1B5E20;">
                <p style='font-size: 1.2rem; text-align: center;'>
                    💡 Doğru cevap: {current['text']}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Updated keyboard shortcuts info
        with st.expander("⌨️ Klavye Kısayolları"):
            st.markdown("""
            - `Ctrl + Enter`: Cevabı kontrol et
            - `→` (Sağ Ok): Sonraki cümle
            - `←` (Sol Ok): Önceki cümle
            - `Ctrl + Space`: Cevabı göster/gizle
            - `Shift + Enter`: Yeni satır
            """)
        
        # Save progress
        save_progress(st.session_state.sentence_data, 
                     st.session_state.current_index,
                     st.session_state.translations)
    
    else:
        st.info("👈 Başlamak için sol menüden bir altyazı dosyası yükleyin.")
        
        with st.expander("ℹ️ Nasıl Kullanılır?"):
            st.markdown("""
            1. Sol menüden bir .srt uzantılı altyazı dosyası yükleyin
            2. Türkçe çevirisi verilen cümleyi İngilizce olarak yazın
            3. 'Kontrol Et' butonuna tıklayarak veya Ctrl+Enter tuşuna basarak cevabınızı kontrol edin
            4. İsterseniz 'Cevabı Göster' butonu ile veya Ctrl+Space tuşu ile doğru cevabı görebilirsiniz
            5. Sağ/Sol ok tuşları ile cümleler arasında gezinebilirsiniz
            """)

if __name__ == '__main__':
    main()