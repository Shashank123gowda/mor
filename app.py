import os
import re
from datetime import date, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_dates(days: int = 60):
    # Today through next `days` days inclusive
    today = date.today()
    return [today + timedelta(days=i) for i in range(days + 1)]


def find_existing_for_date(d: date):
    base = d.strftime("%Y-%m-%d")
    for ext in ALLOWED_EXTENSIONS:
        candidate = f"{base}.{ext}"
        if os.path.exists(os.path.join(UPLOAD_FOLDER, candidate)):
            return candidate
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        target_date = request.form.get("date", "").strip()
        file = request.files.get("photo")

        if not target_date or not DATE_RE.match(target_date):
            flash("Invalid date.", "error")
            return redirect(url_for("upload"))

        if not file or file.filename == "":
            flash("Please select a file to upload.", "error")
            return redirect(url_for("upload") + f"#d-{target_date}")

        if not allowed_file(file.filename):
            flash("Unsupported file type. Please upload an image.", "error")
            return redirect(url_for("upload") + f"#d-{target_date}")

        ext = file.filename.rsplit(".", 1)[1].lower()
        save_name = f"{target_date}.{ext}"
        save_path = os.path.join(UPLOAD_FOLDER, save_name)

        # Remove any existing files for this date (other extensions) to keep one per day
        for old_ext in list(ALLOWED_EXTENSIONS):
            old_path = os.path.join(UPLOAD_FOLDER, f"{target_date}.{old_ext}")
            if os.path.exists(old_path) and old_path != save_path:
                try:
                    os.remove(old_path)
                except OSError:
                    pass

        file.save(save_path)
        flash("Photo uploaded successfully!", "success")
        return redirect(url_for("upload") + f"#d-{target_date}")

    # GET
    days = generate_dates(60)  # ~next 2 months
    items = []
    for d in days:
        ds = d.strftime("%Y-%m-%d")
        existing = find_existing_for_date(d)
        items.append({
            "date": ds,
            "existing": existing,
        })
    return render_template("upload.html", items=items)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/views")
def views():
    files = []
    try:
        for name in os.listdir(UPLOAD_FOLDER):
            if not any(name.lower().endswith(f".{ext}") for ext in ALLOWED_EXTENSIONS):
                continue
            base, _ = os.path.splitext(name)
            files.append({"name": name, "date": base})
    except FileNotFoundError:
        pass
    files.sort(key=lambda x: x["date"], reverse=True)
    return render_template("gallery.html", files=files)


if __name__ == "__main__":
    app.run(debug=True)