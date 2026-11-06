# Eslear Book Summarizer

A local Flask website for uploading text-based PDFs or text files, pasting article/newspaper text, extracting important sentences, creating revision flashcards, saving notes, and downloading summaries.

## Features
- Upload PDF, TXT, and Markdown (`.md`) files up to 20 MB.
- Paste text from books, articles, newspapers, or class notes.
- Extractive summarization with a simple word-frequency scoring algorithm.
- Save summaries, key points, flashcards, and notes in SQLite (`easler.db`).
- Click-to-flip flashcards, browser text-to-speech, and `.txt` export.
- Responsive HTML5/Jinja2 interface with vanilla CSS and JavaScript.

## Requirements
- Python 3.10+ recommended
- VS Code
- Internet connection for the first `pip install`; Google Fonts are optional at runtime.

## Run in VS Code (Windows)
1. Extract `Eslear_Book_Summarizer.zip`.
2. Open the extracted `Eslear_Book_Summarizer` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:
   ```powershell
   py -m venv .venv
   ```
5. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt and run `.venv\\Scripts\\activate.bat`.
6. Install packages:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
7. Start the website:
   ```powershell
   python app.py
   ```
8. Open `http://127.0.0.1:5000` in your browser.
9. Upload a text-based PDF/TXT/MD or paste article text. Open a generated summary to review key points, flip cards, save notes, or export.

## Project structure
```text
Eslear_Book_Summarizer/
├── app.py
├── summarizer.py
├── requirements.txt
├── easler.db             # created automatically on first run; not included
├── uploads/              # temporary uploads are deleted after extraction
├── templates/
│   ├── base.html
│   ├── index.html
│   └── summary.html
└── static/
    ├── style.css
    └── app.js
```

## How it works
1. Flask receives a file or pasted text.
2. `pypdf` extracts selectable text from PDFs; TXT/MD files are read as UTF-8.
3. The summarizer splits the text into sentences, scores them using non-stopword frequency, and selects the highest scoring sentences while retaining their original order.
4. The app stores the original text, summary, key points, flashcards, and notes in SQLite.
5. JavaScript powers flashcard flipping, browser speech synthesis, and text-file export.

## Limitations and future improvements
- This is an educational starter project, not a production-ready AI summarizer. It uses extractive ranking, not a generative language model; selected sentences can miss context or include less-important details.
- Scanned/image-only PDFs need OCR; this version supports text-based PDFs only.
- PDF.js is not included because the backend uses `pypdf` to extract PDF text. It can be added for browser-side PDF preview if needed.
- For production, add authentication, CSRF protection, rate limiting, virus scanning, secure secret management, retention controls, and deployment configuration.
- Uploaded files are deleted after text extraction; extracted text is stored in the local SQLite database until a summary is deleted.
