from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import os
import subprocess
from datetime import datetime
from utils.types import Joint
from utils.types.sport import ALL_SPORTS, ALL_MOVEMENTS
from pipeline.run_pipeline import run_analysis
import threading
import json
import mimetypes
from pathlib import Path
import shutil
from utils.dir_manager import DirectoryManager

app = Flask(__name__)
app.secret_key = "dev"  # replace in production

APP_DATA = Path(app.root_path).parent / "app-data"
app.config["UPLOAD_FOLDER"] = APP_DATA / "cache"
app.config["HISTORY_FOLDER"] = APP_DATA / "history"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["HISTORY_FOLDER"], exist_ok=True)

# ✅ ADD THIS LINE
DirectoryManager.init_paths(
    cache_dir=app.config["UPLOAD_FOLDER"],
    history_dir=app.config["HISTORY_FOLDER"]
)

active_jobs = {}


ALLOWED_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
def is_valid_video(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def handle_video_upload(field_name, filename):
    file = request.files[field_name]
    temp_path = os.path.join(app.config["UPLOAD_FOLDER"], f"temp_{filename}")
    final_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    file.save(temp_path)

    subprocess.run([
        "ffmpeg", "-y",
        "-i", temp_path,
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-shortest",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        final_path
    ], check=True)

    os.remove(temp_path)
    return final_path

def render_edit_video_page(session_key: str, next_route: str, label: str, prefix: str, current_index: int, prev_url=None):
    video_filename = os.path.basename(session[session_key])
    mimetype = mimetypes.guess_type(video_filename)[0] or "video/mp4"
    raw_path = os.path.join(app.config["UPLOAD_FOLDER"], video_filename)

    return render_template(
        "edit_video.html",
        video_path=url_for('serve_video', filename=video_filename),
        mimetype=mimetype,
        raw_path=raw_path,
        next_url=url_for(next_route),
        prefix=prefix,
        label=label,
        show_progress=True,
        current_index=current_index,
        prev_url=prev_url
    )

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/analyze/sport", methods=["GET", "POST"])
def select_sport():
    if request.method == "POST":
        sport_key = request.form.get("sport")
        if sport_key not in ALL_SPORTS:
            flash("Invalid sport selected.")
            return redirect(request.url)
        session["sport"] = sport_key
        return redirect(url_for("select_movement"))

    return render_template("select_sport.html", sports=ALL_SPORTS.values(), show_progress=True, current_index=0)

@app.route("/analyze/movement", methods=["GET", "POST"])
def select_movement():
    sport_key = session.get("sport")
    sport = ALL_SPORTS.get(sport_key)

    if not sport:
        return redirect(url_for("select_sport"))

    if request.method == "POST":
        movement_key = request.form.get("movement")
        if movement_key not in [m.key for m in sport.movements]:
            flash("Invalid movement selected.")
            return redirect(request.url)
        session["movement"] = movement_key
        return redirect(url_for("upload_user_video"))

    return render_template("select_movement.html", sport=sport, show_progress=True, current_index=1)

@app.route("/analyze/user-upload", methods=["GET", "POST"])
def upload_user_video():
    if request.method == "POST":
        file = request.files.get("user_video")
        if not file or file.filename == "":
            flash("Please upload a valid video file.")
            return redirect(request.url)

        if not is_valid_video(file.filename):
            flash("Unsupported video format.")
            return redirect(request.url)

        session["user_video"] = handle_video_upload("user_video", "user_upload.mp4")
        return redirect(url_for("edit_user_video"))

    return render_template("upload_user_video.html", show_progress=True, current_index=2)

@app.route("/video/<path:filename>")
def serve_video(filename):
    full_path = Path(app.root_path).parent / app.config["UPLOAD_FOLDER"] / filename
    full_path = str(full_path)

    guessed_mime = mimetypes.guess_type(full_path)[0] or "video/mp4"
    print(f"📦 Serving video file: {full_path}")
    print(f"📎 Guessed MIME type: {guessed_mime}")
    print(f"📏 File exists? {os.path.exists(full_path)}")

    return send_file(full_path, mimetype=guessed_mime)

@app.route("/analyze/user-edit", methods=["GET", "POST"])
def edit_user_video():
    if request.method == "POST":
        session["user_trim"] = (request.form["user_trim_start"], request.form["user_trim_end"])
        session["user_crop"] = (
            request.form["user_crop_x"], request.form["user_crop_y"],
            request.form["user_crop_w"], request.form["user_crop_h"]
        )
        return redirect(url_for("select_comparison_video"))

    return render_edit_video_page("user_video", "select_comparison_video", "Your Video", "user", current_index=3, prev_url="upload_user_video")

@app.route("/analyze/comparison", methods=["GET", "POST"])
def select_comparison_video():
    if request.method == "POST":
        source = request.form.get("source")
        if source == "upload":
            file = request.files.get("comparison_video")
            if not file or not is_valid_video(file.filename):
                flash("Please upload a valid comparison video.")
                return redirect(request.url)
            path = handle_video_upload("comparison_video", "comparison_upload.mp4")
            session["comparison_video"] = path
        else:
            session["comparison_video"] = os.path.join("static/comparisons", request.form.get("preset_video"))

        return redirect(url_for("edit_comparison_video"))

    return render_template("select_comparison_video.html", show_progress=True, current_index=4)

@app.route("/analyze/comparison-edit", methods=["GET", "POST"])
def edit_comparison_video():
    if request.method == "POST":
        session["comparison_trim"] = (request.form["comparison_trim_start"], request.form["comparison_trim_end"])
        session["comparison_crop"] = (
            request.form["comparison_crop_x"], request.form["comparison_crop_y"],
            request.form["comparison_crop_w"], request.form["comparison_crop_h"]
        )
        return redirect(url_for("run_analysis_page"))

    return render_edit_video_page("comparison_video", "run_analysis_page", "Comparison Video", "comparison", current_index=5, prev_url="select_comparison_video")

@app.route("/analyze/run")
def run_analysis_page():
    job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session["job_id"] = job_id
    DirectoryManager.set_job(job_id)
    active_jobs[job_id] = {
        "status": "running",
        "step": "Queued",
        "steps_log": ["Queued"]
    }
    movement_key = session.get("movement")
    user_path = session.get("user_video")
    trim_user = session.get("user_trim")
    crop_user = session.get("user_crop")
    comp_path = session.get("comparison_video")
    trim_comp = session.get("comparison_trim")
    crop_comp = session.get("comparison_crop")
    selected_joints = [Joint(j) for j in ALL_MOVEMENTS[movement_key].joints]

    def background_task():
        try:
            run_analysis(
                movement_key=movement_key,
                user_path=user_path,
                trim_user=trim_user,
                crop_user=crop_user,
                comp_path=comp_path,
                trim_comp=trim_comp,
                crop_comp=crop_comp,
                selected_joints=selected_joints,
                job=active_jobs[job_id]
            )

            active_jobs[job_id]["status"] = "done"

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print("❌ Error during analysis:\n", error_trace)

            active_jobs[job_id]["status"] = "error"
            active_jobs[job_id]["error"] = str(e)
            active_jobs[job_id]["traceback"] = error_trace

    thread = threading.Thread(target=background_task)
    thread.start()

    return render_template("loading.html", job_id=job_id, show_progress=True, current_index=6)

@app.route("/analyze/status/<job_id>")
def job_status(job_id):
    job = active_jobs.get(job_id)
    if not job:
        return {"status": "unknown"}, 404
    return {
        "status": job["status"],
        "step": job.get("step", ""),
        "steps_log": job.get("steps_log", [])
    }

@app.route("/analyze/results")
def show_results():
    job_id = session.get("job_id")
    job = active_jobs.get(job_id)

    if not job or job["status"] != "done":
        return redirect(url_for("run_analysis_page"))

    result_dir = DirectoryManager.get_run_dir()
    feedback_text = DirectoryManager.get_feedback_text() or ""

    return render_template("results.html", result_dir=result_dir, feedback_text=feedback_text, show_progress=True, current_index=7)

@app.route("/analyze/save", methods=["POST"])
def save_run():
    run_name = request.form.get("run_name")
    if not run_name:
        flash("Run name is required.")
        return redirect(url_for("show_results"))

    success = DirectoryManager.save_to_history(run_name, overwrite=True)
    if not success:
        flash("Run could not be saved.")
    else:
        flash(f"Run saved as '{run_name}'.")

    return redirect(url_for("history"))

@app.route("/cache/<path:filename>")
def serve_cache_file(filename):
    full_path = app.config["UPLOAD_FOLDER"] / filename
    full_path = str(full_path)
    if not os.path.exists(full_path):
        return "File not found", 404
    guessed_mime = mimetypes.guess_type(full_path)[0] or "application/octet-stream"
    return send_file(full_path, mimetype=guessed_mime)

@app.route("/history")
def history():
    history_dir = app.config["HISTORY_FOLDER"]
    jobs = []

    for job_id in sorted(os.listdir(history_dir), reverse=True):
        job_path = os.path.join(history_dir, job_id)
        metadata_path = os.path.join(job_path, "metadata.json")

        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                meta = json.load(f)
            jobs.append({
                "job_id": job_id,
                "timestamp": meta.get("timestamp"),
                "sport": meta.get("sport"),
                "movement": meta.get("movement"),
                "joints": meta.get("joints"),
                "video_file": f"/{job_path}/" + meta.get("video_file", "combined.mp4")
            })

    return render_template("history.html", jobs=jobs)

@app.route("/history/<job_id>")
def show_past_results(job_id):
    job_path = os.path.join(app.config["HISTORY_FOLDER"], job_id)
    if not os.path.exists(job_path):
        return "Not Found", 404

    feedback_path = os.path.join(job_path, "llm_feedback.txt")
    feedback_text = ""
    if os.path.exists(feedback_path):
        with open(feedback_path, "r") as f:
            feedback_text = f.read()

    return render_template("results.html", result_dir=job_path, feedback_text=feedback_text, show_progress=False)

if __name__ == "__main__":
    app.run(debug=True)
