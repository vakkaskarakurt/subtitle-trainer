import pysrt
import chardet
import re
import nltk
from pathlib import Path

def get_time_in_seconds(time_str):
    """Zaman string'ini saniyeye çevir"""
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

def format_seconds_to_time(seconds):
    """Saniyeyi zaman string'ine çevir"""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def detect_encoding(file_content):
    """Dosya kodlamasını tespit et"""
    result = chardet.detect(file_content)
    return result['encoding']

def read_srt_file(file_content):
    """SRT dosyasını oku"""
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1', 'iso-8859-9', 
                'cp1252', 'cp1254', 'ascii', 'utf-16', 'utf-32']
    
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
    """Altyazıları cümlelere ayır"""
    combined_text = ""
    current_sentence_start = None
    temp_subtitle_data = []
    
    for sub in subs:
        text = sub.text.strip()
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