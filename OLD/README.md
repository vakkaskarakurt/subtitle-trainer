# subtitle-trainer
A PyQt6-based subtitle trainer that helps users improve their English by practicing sentences from .srt files. It provides real-time feedback, similarity analysis, automatic translations, and progress tracking.

## Features
- 📂 **Load Subtitle Files**: Select `.srt` files for practice.
- 📝 **Sentence Completion**: Type in the correct English translation.
- ✅ **Instant Feedback**: String similarity and semantic comparison.
- 🌍 **Automatic Translation**: Provides Turkish translations for reference.
- 🔢 **Progress Tracking**: Displays completion progress and estimated time.
- 🎯 **Keyboard Shortcuts**:
  - `Enter`: Check the answer
  - `→` (Right Arrow): Next sentence
  - `←` (Left Arrow): Previous sentence
  - `Space`: Show/hide the correct answer
  - `Shift + Enter`: Add a new line

## Installation
python -m venv venv
pip install -r requirements.txt

python -m spacy download en_core_web_md 
python -m nltk.downloader punkt 

### Prerequisites
Ensure you have Python installed (preferably 3.11.4). Install the required dependencies:

```bash
pip install PyQt6 pysrt deep-translator nltk spacy translate
python -m spacy download en_core_web_md