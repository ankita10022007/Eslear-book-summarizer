"""Lightweight extractive summarization; no external AI API is required."""
from pathlib import Path
import re
from collections import Counter

STOPWORDS = set("""
a an the and or but if while is are was were be been being to of in on for from by with
as at this that these those it its into about over after before between through during
not no can could should would may might will shall do does did have has had having we they
them their you your he she his her i me my our us which who what when where why how than
then also very more most some any each other such only own same so too just
""".split())


def extract_text(path):
    path = Path(path)
    ext = path.suffix.lower()
    if ext == ".pdf":
        try:
            import pypdf
        except ImportError as exc:
            raise RuntimeError("PDF support dependency missing. Run: pip install -r requirements.txt") from exc
        reader = pypdf.PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages)
        if not text.strip():
            raise ValueError("No selectable text found. Scanned PDFs need OCR, which this starter version does not include.")
        return text
    return path.read_text(encoding="utf-8", errors="replace")


def sentence_split(text):
    text = re.sub(r"\s+", " ", text).strip()
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“\"'])", text) if len(s.strip()) > 25]


def summarize_text(text, max_points=7):
    sentences = sentence_split(text)
    if not sentences:
        return text[:500], [text[:240]]
    words = re.findall(r"\b[a-zA-Z][a-zA-Z'-]{2,}\b", text.lower())
    freq = Counter(w for w in words if w not in STOPWORDS)
    if not freq:
        selected = sentences[:max_points]
    else:
        max_freq = max(freq.values())
        weights = {w: count / max_freq for w, count in freq.items()}
        scored = []
        for i, sentence in enumerate(sentences):
            tokens = re.findall(r"\b[a-zA-Z][a-zA-Z'-]{2,}\b", sentence.lower())
            score = sum(weights.get(w, 0) for w in tokens) / max(1, len(tokens) ** 0.5)
            # Slightly favor sentences near the beginning, common in articles and reports.
            score += max(0, 0.12 - i * 0.003)
            scored.append((score, i, sentence))
        chosen = sorted(scored, reverse=True)[:max_points]
        selected = [s for _, _, s in sorted(chosen, key=lambda item: item[1])]
    summary = " ".join(selected)
    return summary, selected


def make_flashcards(key_points):
    cards = []
    for point in key_points:
        cleaned = point.strip()
        if cleaned:
            words = cleaned.split()
            question = "What is the key idea?"
            if len(words) > 7:
                question = "Explain this point: " + " ".join(words[:6]) + "…"
            cards.append({"question": question, "answer": cleaned})
    return cards
