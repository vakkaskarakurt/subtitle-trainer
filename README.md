# 🎬 Subtitle Trainer

**An interactive desktop application that transforms .srt subtitle files into an immersive English language learning experience.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)

---

## 🌟 Overview

**Subtitle Trainer** turns your favorite movies and shows into personalized English practice sessions. Load any `.srt` subtitle file and get instant feedback on your translations using advanced NLP techniques.

### 💡 The Problem
- Traditional language apps use generic, boring sentences
- Watching movies passively doesn't improve speaking/writing skills
- No immediate feedback on language production

### ✅ The Solution
- Practice with **real dialogues** from content you love
- Get **instant feedback** using similarity analysis and semantic comparison
- Track your progress with built-in metrics
- Learn contextually with automatic translations

---

## ✨ Key Features

### 🎯 Core Functionality
- **📂 Subtitle File Support**: Load any standard `.srt` file
- **✍️ Interactive Practice**: Type English translations sentence by sentence
- **🔍 Dual Analysis System**:
  - **String Similarity**: Levenshtein distance for typo tolerance
  - **Semantic Similarity**: spaCy word embeddings for meaning comparison
- **🌍 Smart Translations**: Automatic Turkish translations via Google Translate API
- **📊 Progress Tracking**: Real-time completion percentage and time estimates

### ⌨️ Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Enter` | Check your answer |
| `→` | Next sentence |
| `←` | Previous sentence |
| `Space` | Toggle correct answer visibility |
| `Shift + Enter` | New line in text input |

### 🎨 User Experience
- Clean, modern PyQt6 interface
- Color-coded feedback (🟢 green = correct, 🟡 yellow = close, 🔴 red = incorrect)
- Sentence context display
- Progress bar with ETA

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **GUI Framework** | PyQt6 |
| **NLP** | spaCy (en_core_web_md), NLTK |
| **Translation** | deep-translator, translate |
| **Subtitle Parsing** | pysrt |
| **String Analysis** | Levenshtein distance (difflib) |

---

## 🚀 Installation

### Prerequisites
- Python 3.11+ (tested on 3.11.4)
- pip package manager

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/vakkaskarakurt/subtitle-trainer.git
cd subtitle-trainer
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download NLP models**
```bash
# Download spaCy English model
python -m spacy download en_core_web_md

# Download NLTK data
python -m nltk.downloader punkt
```

5. **Run the application**
```bash
python subtitle-trainer.py
```

---

## 📖 Usage

### Basic Workflow

1. **Launch** the application
2. **Click "Select Subtitle File"** and choose a `.srt` file
3. **Read** the Turkish sentence displayed
4. **Type** the English translation in the text box
5. **Press Enter** to check your answer
6. **Review** feedback:
   - 🟢 **Green**: Perfect match (90%+ similarity)
   - 🟡 **Yellow**: Close (70-90% similarity)
   - 🔴 **Red**: Needs improvement (<70%)
7. **Navigate** with arrow keys or buttons
8. **Track** your progress in the status bar

---

## 🧠 How It Works

### Similarity Analysis Algorithm

The app uses a **dual-scoring system** for maximum accuracy:

1. **String Similarity (Levenshtein Distance)**
   - Handles typos and minor spelling errors
   - Uses Python's `difflib.SequenceMatcher`

2. **Semantic Similarity (Word Embeddings)**
   - Understands meaning even with different word choices
   - Powered by spaCy's `en_core_web_md` model

3. **Final Score**
   - Weighted average: 70% string similarity + 30% semantic similarity
   - Provides tolerance for stylistic variations

### Translation Pipeline

```
.srt file → pysrt parser → Sentence extraction → 
Google Translate API → Turkish display → 
User input → Similarity analysis → Feedback
```

---

## 🎯 Use Cases

### For Language Learners
- **Practice writing** English sentences
- **Improve translation skills** from native language
- **Learn vocabulary** in context from real dialogues
- **Build confidence** with immediate feedback

### For Teachers
- **Create custom exercises** from movie dialogues
- **Assign level-appropriate content** based on subtitle difficulty

### For Researchers
- **Test translation quality** by reverse-translation
- **Analyze subtitle accuracy** across different sources

---

## 🚧 Roadmap

Planned enhancements:

- [ ] **Multi-language support** (Spanish, French, German, etc.)
- [ ] **Difficulty levels** (filter sentences by complexity)
- [ ] **Spaced repetition** (SRS algorithm for optimal review)
- [ ] **Statistics dashboard** (track accuracy over time)
- [ ] **Audio integration** (play original audio from video files)
- [ ] **Gamification** (points, streaks, achievements)

---

## 🤝 Contributing

Contributions are welcome! 

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 Requirements

See [`requirements.txt`](requirements.txt):

```
PyQt6>=6.0.0
pysrt>=1.1.2
deep-translator>=1.11.4
nltk>=3.8.1
spacy>=3.7.0
translate>=3.6.1
```

---

## 🐛 Known Issues

- **Translation API limits**: Google Translate may rate-limit after ~100 requests/hour
- **Large subtitle files**: Files with 1000+ sentences may slow down initial loading
- **Special characters**: Some Unicode characters may not display correctly on all systems

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Vakkas Karakurt**

- GitHub: [@vakkaskarakurt](https://github.com/vakkaskarakurt)
- LinkedIn: [vakkaskarakurt](https://linkedin.com/in/vakkaskarakurt)
- Email: karakurtvakkas@gmail.com

---

## 🙏 Acknowledgments

- **spaCy** for robust NLP models
- **PyQt6** for cross-platform GUI framework
- **pysrt** for subtitle parsing
- Inspired by language learning apps like Duolingo and Anki

---

## 🔗 Related Projects

- [YuLaF - YouTube Language Filter](https://github.com/vakkaskarakurt/YuLaF-YouTube-Language-Filter) - Chrome extension for language-based content filtering
- [Word Corrector](https://github.com/vakkaskarakurt/word_corrector_python) - Turkish spell checker with 99.2% accuracy

---

**Made with ❤️ for language learners worldwide**
