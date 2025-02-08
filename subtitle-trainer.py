import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                           QTextEdit, QProgressBar, QMessageBox, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QShortcut, QKeySequence, QFont, QPalette, QColor
import pysrt
from deep_translator import GoogleTranslator, MyMemoryTranslator
from difflib import SequenceMatcher
import nltk
import re
import spacy
import random
import time
from translate import Translator


class SubtitleLearningApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("İngilizce Altyazı Öğrenme Programı")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Window size policy
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        # Initialize spaCy
        try:
            self.nlp = spacy.load('en_core_web_md')
        except:
            QMessageBox.information(self, "Model Yükleniyor", "İlk kullanım için dil modeli indiriliyor...")
            import os
            os.system('python -m spacy download en_core_web_md')
            self.nlp = spacy.load('en_core_web_md')
            
        # Set default window size based on screen size
        screen = QApplication.primaryScreen().size()
        self.resize(int(screen.width() * 0.7), int(screen.height() * 0.7))
        
        # Initialize state
        self.sentence_data = []
        self.translations = {}
        self.current_index = 0
        self.show_answer = False
        self.total_duration = 0
        
        # Setup UI
        self.setup_ui()
        self.setup_shortcuts()
        self.setup_dark_theme()
        
        # Install event filters for TextEdits
        self.answer_input.installEventFilter(self)
        self.jump_input.installEventFilter(self)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Screen-based dynamic sizing
        screen_height = QApplication.primaryScreen().size().height()
        base_font_size = int(screen_height * 0.015)  # Ekran yüksekliğine göre temel font boyutu
        
        # Setup fonts
        title_font = QFont()
        title_font.setPointSize(base_font_size + 2)
        title_font.setBold(True)
        
        normal_font = QFont()
        normal_font.setPointSize(base_font_size)
        
        button_font = QFont()
        button_font.setPointSize(base_font_size)
        button_font.setBold(True)
        
        translation_font = QFont()
        translation_font.setPointSize(base_font_size + 4)
        translation_font.setBold(True)
        
        # Layout settings
        main_layout.setSpacing(1)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # File selection button
        self.file_button = QPushButton("İngilizce Altyazı Seç (.srt)")
        self.file_button.setFont(button_font)
        self.file_button.setMinimumHeight(50)
        self.file_button.clicked.connect(self.load_subtitle_file)
        main_layout.addWidget(self.file_button)
        
        # Progress frame
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        progress_frame.setMinimumHeight(100)
        progress_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 10px;
                margin: 5px 0px;
            }
        """)
        progress_layout = QHBoxLayout(progress_frame)
        
        # Progress labels and bars
        self.progress_label = QLabel("İlerleme: 0/0")
        self.time_label = QLabel("⏱️ 00:00:00 → 00:00:00")
        
        for label, name in [(self.progress_label, "progress"), 
                          (self.time_label, "time")]:
            label_layout = QVBoxLayout()
            label.setFont(button_font)
            label.setStyleSheet("color: #ffffff;")
            label_layout.addWidget(label)
            
            progress_bar = QProgressBar()
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #2a2a2a;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #424242;
                    height: 12px;
                }
                QProgressBar::chunk {
                    background-color: #2196F3;
                    border-radius: 3px;
                }
            """)
            progress_bar.setTextVisible(False)
            setattr(self, f"{name}_bar", progress_bar)
            label_layout.addWidget(progress_bar)
            
            progress_layout.addLayout(label_layout)
        
        main_layout.addWidget(progress_frame)
        
        # Translation section
        translation_label = QLabel("Türkçe Metin:")
        translation_label.setFont(title_font)
        main_layout.addWidget(translation_label)
        
        self.translation_label = QLabel()
        self.translation_label.setFont(translation_font)
        self.translation_label.setMinimumHeight(100)
        self.translation_label.setMaximumHeight(200)
        self.translation_label.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                padding: 20px;
                border-radius: 15px;
                border: 2px solid #3a3a3a;
            }
        """)
        self.translation_label.setWordWrap(True)
        self.translation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.translation_label)
        
        # Answer section
        answer_label = QLabel("İngilizce cümleyi yazın:")
        answer_label.setFont(title_font)
        main_layout.addWidget(answer_label)
        
        # Answer input
        self.answer_input = QTextEdit()
        self.answer_input.setFont(translation_font)
        self.answer_input.setMinimumHeight(100)
        self.answer_input.setMaximumHeight(200)
        self.answer_input.setStyleSheet("""
            QTextEdit {
                padding: 15px;
                border-radius: 8px;
                background-color: #2a2a2a;
                font-weight: bold;
                margin: 10px 0;
            }
        """)
        main_layout.addWidget(self.answer_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 10, 0, 10)
        
        self.check_button = QPushButton("✓ Kontrol Et")
        self.show_answer_button = QPushButton("👁 Cevabı Göster")
        
        for button in [self.check_button, self.show_answer_button]:
            button.setFont(button_font)
            button.setMinimumHeight(60)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    border-radius: 10px;
                    border: none;
                    color: white;
                    padding: 15px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
            """)
        
        self.check_button.clicked.connect(self.check_answer)
        self.show_answer_button.clicked.connect(self.toggle_answer)
        
        button_layout.addWidget(self.check_button)
        button_layout.addWidget(self.show_answer_button)
        main_layout.addLayout(button_layout)
        
        # Answer display
        self.answer_label = QLabel()
        self.answer_label.setFont(QFont('Arial', base_font_size + 2, QFont.Weight.Bold))
        self.answer_label.setMinimumHeight(60)
        self.answer_label.setStyleSheet("""
            QLabel {
                color: white;
                padding: 15px;
                background-color: #2a2a2a;
                border-radius: 8px;
                margin: 10px 0;
                border: 2px solid #3a3a3a;
            }
        """)
        self.answer_label.setWordWrap(True)
        self.answer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.answer_label)
        
        # Current answer display
        self.current_answer_label = QLabel()
        self.current_answer_label.setFont(normal_font)
        self.current_answer_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                padding: 10px;
                min-height: 30px;
            }
        """)
        self.current_answer_label.setWordWrap(True)
        main_layout.addWidget(self.current_answer_label)
        
        # Words display label
        self.words_label = QLabel()
        self.words_label.setFont(QFont('Arial', base_font_size - 2))
        self.words_label.setMinimumHeight(50)
        self.words_label.setStyleSheet("""
            QLabel {
                color: #9e9e9e;
                background-color: #2a2a2a;
                padding: 10px;
                border-radius: 5px;
                margin: 5px 0;
                min-height: 50px;
            }
        """)
        self.words_label.setWordWrap(True)
        self.words_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.words_label)
        
        # Navigation
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)
        nav_layout.setContentsMargins(0, 10, 0, 10)
        
        self.prev_button = QPushButton("◀ Önceki")
        self.next_button = QPushButton("▶ Sonraki")
        
        # Jump input
        self.jump_input = QTextEdit()
        self.jump_input.setPlaceholderText("Altyazı No")
        self.jump_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.jump_input.setMaximumWidth(100)
        self.jump_input.setMaximumHeight(40)
        self.jump_input.setFont(button_font)
        self.jump_input.setStyleSheet("""
            QTextEdit {
                background-color: #424242;
                border-radius: 5px;
                padding: 5px;
                color: white;
            }
        """)
        
        for button in [self.prev_button, self.next_button]:
            button.setFont(button_font)
            button.setMinimumHeight(40)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #424242;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #616161;
                }
                QPushButton:disabled {
                    background-color: #2a2a2a;
                }
            """)
        
        self.prev_button.clicked.connect(self.prev_sentence)
        self.next_button.clicked.connect(self.next_sentence)
        
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.jump_input)
        nav_layout.addWidget(self.next_button)
        main_layout.addLayout(nav_layout)
        
        # Shortcuts info
        shortcuts_label = QLabel(
            "Kısayollar: Enter: Kontrol et | →: Sonraki | ←: Önceki | Space: Cevabı göster/gizle | Shift+Enter: Yeni satır"
        )
        shortcuts_label.setFont(normal_font)
        shortcuts_label.setStyleSheet("color: #757575;")
        main_layout.addWidget(shortcuts_label)
        
        # Add stretch to push everything up
        main_layout.addStretch(1)

    def setup_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(127, 127, 127))
        QApplication.instance().setPalette(palette)

    def setup_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, activated=self.next_sentence)
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, activated=self.prev_sentence)
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, activated=self.toggle_answer)

    def eventFilter(self, obj, event):
        if event.type() == event.Type.KeyPress and event.key() == Qt.Key.Key_Return:
            modifiers = event.modifiers()
            
            # Enter tuşuna basıldığında
            if modifiers == Qt.KeyboardModifier.NoModifier:
                if obj == self.answer_input:
                    self.check_answer()
                    return True
                elif obj == self.jump_input:
                    self.jump_to_subtitle()
                    return True
            
            # Shift + Enter tuşuna basıldığında
            elif modifiers == Qt.KeyboardModifier.ShiftModifier:
                cursor = obj.textCursor()
                cursor.insertText('\n')
                return True
                
        return super().eventFilter(obj, event)

    def check_answer(self):
        if not self.sentence_data:
            return
                
        answer = self.answer_input.toPlainText().strip()
        current = self.sentence_data[self.current_index]['text'].strip()
        
        if answer and current:
            # Remove punctuation and extra spaces for string comparison
            def clean_text(text):
                # Remove punctuation and convert to lowercase
                text = re.sub(r'[^\w\s]', '', text)
                # Remove extra spaces and trim
                text = ' '.join(text.lower().split())
                return text
                    
            clean_answer = clean_text(answer)
            clean_current = clean_text(current)
                
            # String similarity with cleaned text
            string_similarity = SequenceMatcher(None, clean_answer, clean_current).ratio()
                
            # Semantic similarity with original text
            try:
                doc1 = self.nlp(answer.lower())
                doc2 = self.nlp(current.lower())
                semantic_similarity = doc1.similarity(doc2)
                similarity_msg = f"String Benzerliği: {string_similarity:.1%}\nAnlamsal Benzerlik: {semantic_similarity:.1%}"
            except:
                similarity_msg = f"String Benzerliği: {string_similarity:.1%}"
                
            if string_similarity == 1.0:
                self.answer_label.setText(f"✅ Doğru!\n{similarity_msg}")
                self.answer_label.setStyleSheet("color: #4CAF50;")
                    
                QTimer.singleShot(1500, lambda: self.next_sentence() 
                                if self.current_index < len(self.sentence_data) - 1 
                                else None)
                    
                self.answer_input.clear()
                self.show_answer = False
            else:
                # Önce benzerlik bilgisini göster
                self.answer_label.setText(f"❌ Tekrar deneyin\n{similarity_msg}")
                self.answer_label.setStyleSheet("color: #f44336;")

            # Her kontrol sonrası kelime analizi yap
            # Hedef cümledeki kelimeleri sıralı olarak al
            target_words_ordered = re.findall(r'\b\w+\b', current.lower())
            user_words_ordered = re.findall(r'\b\w+\b', answer.lower())

            # Eksik kelimeleri sıralı bulmak için
            missing_words = [word for word in target_words_ordered if word not in set(user_words_ordered)]
            # Fazladan kelimeleri sıralı bulmak için
            extra_words = [word for word in user_words_ordered if word not in set(target_words_ordered)]

            result_text = []

            if missing_words:
                # Sıralı eksik kelimeler
                result_text.append(f"❌ Eksik kelimeler: {' • '.join(missing_words)}")

            if extra_words:
                # Sıralı fazladan kelimeler 
                result_text.append(f"⚠️ Fazladan kullanılan kelimeler: {' • '.join(extra_words)}")
                
            if not missing_words and not extra_words and user_words_ordered:
                result_text.append('Tüm kelimeleri doğru kullanmışsınız! ✨')
                
            self.words_label.setText('\n'.join(result_text))

    def load_subtitle_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Subtitle File",
            "",
            "Subtitle Files (*.srt)"
        )
        
        if file_name:
            # Denenecek encoding'ler
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1', 'iso-8859-9', 
                        'cp1252', 'cp1254', 'ascii', 'utf-16', 'utf-32']
            
            for encoding in encodings:
                try:
                    with open(file_name, 'r', encoding=encoding) as file:
                        content = file.read()
                        
                    # BOM karakterlerini temizle
                    if content.startswith('\ufeff'):
                        content = content[1:]
                    
                    # Geçersiz karakterleri temizle
                    content = ''.join(char for char in content if ord(char) < 65536)
                    
                    subs = pysrt.from_string(content)
                    
                    self.sentence_data = self.process_subtitles(subs)
                    
                    if self.sentence_data:
                        self.total_duration = self.sentence_data[-1]['end_seconds']
                        self.current_index = 0
                        self.show_answer = False
                        self.update_ui()
                        self.load_current_translation()
                        return  # Başarılı okuma
                    else:
                        continue  # Altyazı bulunamadı, diğer encoding'i dene
                        
                except UnicodeDecodeError:
                    continue  # Bu encoding ile açılamadı, diğerini dene
                except Exception as e:
                    continue  # Diğer hatalar için de diğer encoding'i dene
            
            # Hiçbir encoding işe yaramadıysa
            QMessageBox.critical(self, "Hata", 
                "Altyazı dosyası hiçbir karakter kodlaması ile açılamadı. "
                "Lütfen dosyanın bozuk olmadığından emin olun.")

# Önce gerekli kütüphaneyi kurmamız gerekiyor:
# pip install transformers sentencepiece

    def load_current_translation(self):
        if not self.sentence_data:
            return
                
        current_sentence = self.sentence_data[self.current_index]
        current_sentence['text'] = current_sentence['text'].replace('\n', ' ')
        
        if current_sentence['text'] not in self.translations:
            try:
                
                # Çevirmen nesnesini oluştur
                translator = Translator(to_lang="tr", from_lang="en")
                
                # Çeviriyi yap
                translation = translator.translate(current_sentence['text'])
                
                if translation:
                    self.translations[current_sentence['text']] = translation
                else:
                    self.translations[current_sentence['text']] = "Çeviri yapılamadı."
                    
            except Exception as e:
                QMessageBox.warning(self, "Çeviri Hatası", 
                    "Çeviri yapılamadı. Lütfen internet bağlantınızı kontrol edin.")
                self.translations[current_sentence['text']] = "Çeviri hatası oluştu."
            
            self.update_ui()
    def update_ui(self):
        if not self.sentence_data:
            return
                
        total_sentences = len(self.sentence_data)
        current_sentence = self.sentence_data[self.current_index]
        
        # Update progress
        self.progress_label.setText(f"İlerleme: {self.current_index + 1}/{total_sentences}")
        self.progress_bar.setValue(int((self.current_index + 1) / total_sentences * 100))
        
        # Update time progress
        current_time = current_sentence['start_seconds']
        progress_percentage = (current_time / self.total_duration * 100) if self.total_duration > 0 else 0
        self.time_bar.setValue(int(progress_percentage))
        
        # Update time label
        self.time_label.setText(f"⏱️ {current_sentence['start']} → {self.format_seconds_to_time(self.total_duration)}")
        
        # Update translation
        if current_sentence['text'] in self.translations:
            self.translation_label.setText(self.translations[current_sentence['text']])
            self.translation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Show/hide answer
        if self.show_answer:
            self.current_answer_label.setText(f"💡 Doğru cevap: {current_sentence['text']}")
        else:
            self.current_answer_label.clear()
        
        # Clear words
        self.words_label.clear()
        
        # Update navigation buttons
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < total_sentences - 1)
        
        # Focus on input
        self.answer_input.setFocus()
   
    def next_sentence(self):
        if self.current_index < len(self.sentence_data) - 1:
            self.current_index += 1
            self.show_answer = False
            self.answer_input.clear()
            self.load_current_translation()
            self.update_ui()

    def prev_sentence(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_answer = False
            self.answer_input.clear()
            self.load_current_translation()
            self.update_ui()

    def toggle_answer(self):
        self.show_answer = not self.show_answer
        self.update_ui()
        
    def jump_to_subtitle(self):
        try:
            text = self.jump_input.toPlainText().strip()
            target_index = int(text) - 1
            if 0 <= target_index < len(self.sentence_data):
                self.current_index = target_index
                self.show_answer = False
                self.answer_input.clear()
                self.jump_input.clear()
                self.load_current_translation()
                self.update_ui()
            else:
                QMessageBox.warning(self, "Uyarı", f"Lütfen 1 ile {len(self.sentence_data)} arasında bir sayı girin.")
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir sayı girin.")

    def get_time_in_seconds(self, time_str):
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s

    def format_seconds_to_time(self, seconds):
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Right:
            self.next_sentence()
            event.accept()
        elif event.key() == Qt.Key.Key_Left:
            self.prev_sentence()
            event.accept()
        elif event.key() == Qt.Key.Key_Space:
            self.toggle_answer()
            event.accept()
        else:
            super().keyPressEvent(event)

    def process_subtitles(self, subs):
        """Combine subtitles into complete sentences using NLTK sentence tokenizer"""
        combined_text = ""
        current_sentence_start = None
        temp_subtitle_data = []
        
        for sub in subs:

            
            text = sub.text.strip()
            # Remove speaker labels and sound effects in parentheses

            text = re.sub(r'\([^)]*\)', '', text)
            text = re.sub(r'^[A-Z]+:', '', text)
            text = text.strip()

            # also remove </i> and <i> tags

            # text = text.replace('</i>', '')

            # also remove if </(any char)> and <(any char)> tags

            text = re.sub(r'</[a-zA-Z]>', '', text)

            
            if not text:  # Skip empty subtitles
                continue
            
            if current_sentence_start is None:
                current_sentence_start = {
                    'start': str(sub.start).split(',')[0],
                    'start_seconds': self.get_time_in_seconds(str(sub.start).split(',')[0])
                }
            
            combined_text += " " + text
            
            # Check if this subtitle ends with sentence-ending punctuation
            if text.rstrip()[-1] in '.!?':
                temp_subtitle_data.append({
                    'text': combined_text.strip(),
                    'start': current_sentence_start['start'],
                    'end': str(sub.end).split(',')[0],
                    'start_seconds': current_sentence_start['start_seconds'],
                    'end_seconds': self.get_time_in_seconds(str(sub.end).split(',')[0])
                })
                combined_text = ""
                current_sentence_start = None
        
        # Handle any remaining text
        if combined_text.strip():
            temp_subtitle_data.append({
                'text': combined_text.strip(),
                'start': current_sentence_start['start'],
                'end': str(subs[-1].end).split(',')[0],
                'start_seconds': current_sentence_start['start_seconds'],
                'end_seconds': self.get_time_in_seconds(str(subs[-1].end).split(',')[0])
            })
        
        # Now split into proper sentences using NLTK
        sentence_data = []
        for sub in temp_subtitle_data:
            sentences = nltk.sent_tokenize(sub['text'])
            for sentence in sentences:
                if sentence.strip():  # Only add non-empty sentences
                    sentence_data.append({
                        'text': sentence.strip(),
                        'start': sub['start'],
                        'end': sub['end'],
                        'start_seconds': sub['start_seconds'],
                        'end_seconds': sub['end_seconds']
                    })
        
        return sentence_data

def main():
   app = QApplication(sys.argv)
   
   # Set application-wide font
   default_font = QFont()
   default_font.setPointSize(11)
   app.setFont(default_font)
   
   window = SubtitleLearningApp()
   window.show()
   sys.exit(app.exec())

if __name__ == '__main__':
   main()