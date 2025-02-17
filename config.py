import streamlit as st

PAGE_CONFIG = {
    "page_title": "İngilizce Altyazı Öğrenme Programı",
    "page_icon": "📚",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

CUSTOM_CSS = """
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
    .info-box {
        background-color: #2A2A2A;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #3A3A3A;
        margin: 10px 0;
    }
    
    /* Alert mesajları için yeni stiller */
    .stAlert > div:first-child {
        width: 100% !important;
        min-width: 100% !important;
        padding: 16px !important;
        border-radius: 8px !important;
    }
    
    .stAlert {
        width: 100% !important;
        height: auto !important;
        min-width: 100% !important;
        max-width: 100% !important;
        display: flex !important;
        padding: 0 !important;
    }
    
    .element-container {
        width: 100% !important;
        max-width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    
    div[data-testid="stMarkdownContainer"] > div {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    .stSuccess > div:first-child {
        width: 100% !important;
        background-color: #1B5E20 !important;
    }
    
    .stError > div:first-child {
        width: 100% !important;
        background-color: #B71C1C !important;
    }
</style>
"""