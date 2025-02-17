import streamlit as st
from streamlit_shortcuts import add_keyboard_shortcuts

from config import PAGE_CONFIG, CUSTOM_CSS
from nlp_utils import load_nlp, analyze_answer
from subtitle_processor import read_srt_file, process_subtitles
from ui_components import render_statistics, render_navigation, render_keyboard_shortcuts_info
from state_manager import (
    initialize_session_state, 
    save_progress, 
    load_progress, 
    update_state,
    get_state
)

def setup_page():
    """Sayfa yapılandırmasını ayarla"""
    st.set_page_config(**PAGE_CONFIG)
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def handle_file_upload():
    """Dosya yükleme işlemlerini yönet"""
    uploaded_file = st.sidebar.file_uploader("Altyazı Dosyası Seç (.srt)", type=['srt'])
    
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

def setup_navigation():
    """Navigasyon fonksiyonlarını ayarla"""
    def go_to_next():
        if st.session_state.sentence_data and st.session_state.current_index < len(st.session_state.sentence_data) - 1:
            st.session_state.current_index += 1
            st.session_state.show_answer = False
            st.session_state.update_required = True
            if 'answer_input' in st.session_state:
                del st.session_state.answer_input  # Text input'u temizle

    def go_to_previous():
        if st.session_state.sentence_data and st.session_state.current_index > 0:
            st.session_state.current_index -= 1
            st.session_state.show_answer = False
            st.session_state.update_required = True
            if 'answer_input' in st.session_state:
                del st.session_state.answer_input  # Text input'u temizle

    def toggle_answer():
        if st.session_state.sentence_data:
            st.session_state.show_answer = not st.session_state.show_answer
            st.session_state.update_required = True

    # Klavye kısayollarını ekle
    add_keyboard_shortcuts({
        'ArrowRight': go_to_next,
        'ArrowLeft': go_to_previous,
        'ctrl+Space': toggle_answer,
        'ctrl+Enter': check_answer
    })

    return go_to_next, go_to_previous, toggle_answer

def handle_translation(current_sentence):
    """Çeviri işlemlerini yönet"""
    if current_sentence['text'] not in st.session_state.translations:
        with st.spinner("Çeviri yapılıyor..."):
            st.session_state.translations[current_sentence['text']] = (
                st.session_state.translation_manager.translate(current_sentence['text'])
            )
    
    st.markdown(f"""
    <div class="info-box">
        <p style='font-size: 1.2rem; text-align: center;'>
            {st.session_state.translations[current_sentence['text']]}
        </p>
    </div>
    """, unsafe_allow_html=True)

def check_answer():
    """Kullanıcı cevabını kontrol et"""
    current_input_key = f"answer_input_{st.session_state.current_index}"
    if st.session_state.sentence_data and current_input_key in st.session_state:
        user_answer = st.session_state[current_input_key]
        current = st.session_state.sentence_data[st.session_state.current_index]
        
        st.session_state.statistics['total_attempts'] += 1
        analysis = analyze_answer(user_answer, current['text'], nlp)
        
        if analysis:
            st.session_state.statistics['average_similarity'].append(analysis['string_similarity'])
            
            if analysis['string_similarity'] >= 0.95:  # %95 ve üzeri doğru kabul edilsin
                st.session_state.statistics['correct_answers'] += 1
                st.success(f"""
                ✅ Mükemmel!
                - String Benzerliği: {analysis['string_similarity']:.1%}
                - Anlamsal Benzerlik: {analysis['semantic_similarity']:.1%}
                - Kelime Sırası Doğruluğu: {analysis['word_order_score']:.1%}
                """)
                
                # Otomatik olarak sonraki soruya geç
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
                
                # Detaylı kelime analizi
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

def main():
    """Ana uygulama fonksiyonu"""
    # Sayfa yapılandırması
    setup_page()
    
    # NLP modellerini yükle
    global nlp
    nlp = load_nlp()
    
    # Oturum durumunu başlat
    initialize_session_state()
    
    # Navigasyon fonksiyonlarını ayarla
    go_to_next, go_to_previous, toggle_answer = setup_navigation()
    
    # Sidebar
    with st.sidebar:
        st.title("📚 Kontroller")
        handle_file_upload()
        
        # İstatistikler
        if st.session_state.sentence_data:
            render_statistics(st.session_state.statistics)
            
        # Sidebar'ın en altına boşluk ekle
        st.markdown("<br>" * 5, unsafe_allow_html=True)
        
        # Navigasyon
        if st.session_state.sentence_data:
            st.markdown("---")  # Ayırıcı çizgi
            render_navigation(
                st.session_state.current_index,
                len(st.session_state.sentence_data),
                go_to_previous,
                go_to_next
            )
    
    # Ana içerik
    if st.session_state.sentence_data:
        current = st.session_state.sentence_data[st.session_state.current_index]
        
        # İlerleme çubukları
        col1, col2 = st.columns(2)
        with col1:
            progress = (st.session_state.current_index + 1) / len(st.session_state.sentence_data)
            st.progress(progress, "Genel İlerleme")
            st.caption(f"İlerleme: {st.session_state.current_index + 1}/{len(st.session_state.sentence_data)}")
        
        # Çeviri bölümü
        st.subheader("🌍 Türkçe Metin")
        handle_translation(current)
        
        # Cevap bölümü
        st.subheader("✍️ İngilizce cümleyi yazın")
        # Her cümle için benzersiz bir key oluştur
        input_key = f"answer_input_{st.session_state.current_index}"
        user_answer = st.text_area(
            "",
            key=input_key,
            height=100,
            placeholder="Cevabınızı buraya yazın..."
        )
        
        # Kontrol butonları
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✓ Kontrol Et", key="check_button"):
                check_answer()
        
        with col2:
            if st.button("👁 Cevabı Göster/Gizle", key="toggle_button"):
                toggle_answer()
        
        if st.session_state.show_answer:
            st.markdown(f"""
            <div class="info-box" style="background-color: #1B5E20;">
                <p style='font-size: 1.2rem; text-align: center;'>
                    💡 Doğru cevap: {current['text']}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Ana ekranda navigasyon artık gösterilmeyecek
        
        # Klavye kısayolları bilgisi
        render_keyboard_shortcuts_info()
        
        # İlerlemeyi kaydet
        save_progress(
            st.session_state.sentence_data,
            st.session_state.current_index,
            st.session_state.translations
        )
    
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