from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import sqlite3, os, re, json
from pathlib import Path
from datetime import datetime
from summarizer import extract_text, summarize_text, make_flashcards

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "easler.db"
ALLOWED_EXTENSIONS = {"pdf", "txt", "md"}
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-development-key")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            source_name TEXT NOT NULL,
            source_type TEXT NOT NULL,
            original_text TEXT NOT NULL,
            summary TEXT NOT NULL,
            key_points_json TEXT NOT NULL,
            flashcards_json TEXT NOT NULL,
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )""")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    with get_db() as conn:
        documents = conn.execute(
            "SELECT id, title, source_name, source_type, created_at FROM summaries ORDER BY id DESC"
        ).fetchall()
    return render_template("index.html", documents=documents)


@app.route("/summarize", methods=["POST"])
def summarize():
    uploaded = request.files.get("file")
    pasted_text = request.form.get("article_text", "").strip()
    title = request.form.get("title", "").strip()
    text, source_name, source_type = "", "Pasted text", "text"

    if uploaded and uploaded.filename:
        if not allowed_file(uploaded.filename):
            flash("Please upload a PDF, TXT, or MD file.", "error")
            return redirect(url_for("index"))
        safe_name = secure_filename(uploaded.filename)
        saved_path = UPLOAD_DIR / f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{safe_name}"
        uploaded.save(saved_path)
        source_name = safe_name
        source_type = saved_path.suffix.lower().lstrip(".")
        try:
            text = extract_text(saved_path)
        except Exception as exc:
            saved_path.unlink(missing_ok=True)
            flash(f"Could not read this file: {exc}", "error")
            return redirect(url_for("index"))
        finally:
            saved_path.unlink(missing_ok=True)
    elif pasted_text:
        text = pasted_text
    else:
        flash("Choose a file or paste article/news text first.", "error")
        return redirect(url_for("index"))

    text = re.sub(r"\s+", " ", text).strip()
    if len(text) < 80:
        flash("Please provide at least 80 characters of readable text.", "error")
        return redirect(url_for("index"))

    summary, key_points = summarize_text(text, max_points=7)
    flashcards = make_flashcards(key_points)
    final_title = title or Path(source_name).stem or "Untitled reading"
    with get_db() as conn:
        cur = conn.execute("""INSERT INTO summaries
            (title, source_name, source_type, original_text, summary, key_points_json, flashcards_json, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, '', ?)""",
            (final_title, source_name, source_type, text, summary,
             json.dumps(key_points), json.dumps(flashcards),
             datetime.now().strftime("%Y-%m-%d %H:%M")))
        doc_id = cur.lastrowid
    flash("Summary created. Review the extracted points for accuracy.", "success")
    return redirect(url_for("view_summary", doc_id=doc_id))


@app.route("/summary/<int:doc_id>")
def view_summary(doc_id):
    with get_db() as conn:
        doc = conn.execute("SELECT * FROM summaries WHERE id = ?", (doc_id,)).fetchone()
    if not doc:
        flash("That summary could not be found.", "error")
        return redirect(url_for("index"))
    return render_template("summary.html", doc=doc,
                           key_points=json.loads(doc["key_points_json"]),
                           flashcards=json.loads(doc["flashcards_json"]))


@app.route("/summary/<int:doc_id>/notes", methods=["POST"])
def save_notes(doc_id):
    notes = request.form.get("notes", "")[:10000]
    with get_db() as conn:
        conn.execute("UPDATE summaries SET notes = ? WHERE id = ?", (notes, doc_id))
    flash("Notes saved.", "success")
    return redirect(url_for("view_summary", doc_id=doc_id))


@app.route("/summary/<int:doc_id>/delete", methods=["POST"])
def delete_summary(doc_id):
    with get_db() as conn:
        conn.execute("DELETE FROM summaries WHERE id = ?", (doc_id,))
    flash("Summary deleted.", "success")
    return redirect(url_for("index"))


@app.errorhandler(413)
def too_large(_error):
    flash("File is larger than the 20 MB upload limit.", "error")
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
