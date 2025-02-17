import streamlit as st
from streamlit_shortcuts import button

def render_statistics(stats):
    """İstatistikleri görüntüle"""
    st.subheader("📊 İstatistikler")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Doğru Cevaplar", stats['correct_answers'])
    with col2:
        st.metric("Toplam Deneme", stats['total_attempts'])
    
    if stats['average_similarity']:
        avg_sim = sum(stats['average_similarity']) / len(stats['average_similarity'])
        st.progress(avg_sim, "Ortalama Benzerlik")

def render_navigation(current_index, total_sentences, go_to_previous, go_to_next):
    """Navigasyon kontrollerini görüntüle"""
    st.markdown("### 🎯 Navigasyon")
    col1, col2, col3 = st.columns(3, gap="small")
    
    with col1:
        button("◀ Önceki", "ArrowLeft", 
               go_to_previous,
               disabled=not total_sentences or current_index <= 0,
               hint=True)
    
    with col2:
        if total_sentences:
            jump_to = st.number_input("Altyazı No", 
                min_value=1, 
                max_value=total_sentences,
                value=current_index + 1)
            if jump_to != current_index + 1:
                st.session_state.current_index = jump_to - 1
                st.session_state.show_answer = False

    with col3:
        button("Sonraki ▶", "ArrowRight",
               go_to_next,
               disabled=not total_sentences or current_index >= total_sentences - 1,
               hint=True)

def render_keyboard_shortcuts_info():
    """Klavye kısayolları bilgisini görüntüle"""
    with st.expander("⌨️ Klavye Kısayolları"):
        st.markdown("""
        - `Ctrl + Enter`: Cevabı kontrol et
        - `→` (Sağ Ok): Sonraki cümle
        - `←` (Sol Ok): Önceki cümle
        - `Ctrl + Space`: Cevabı göster/gizle
        - `Shift + Enter`: Yeni satır
        """)