import os
import json
import shutil
from typing import Optional

class DirectoryManager:
    _job_id: Optional[str] = None
    _run_dir: Optional[str] = None
    _cache_dir: Optional[str] = None
    _history_dir: Optional[str] = None

    @classmethod
    def init_paths(cls, cache_dir: str, history_dir: str):
        cls._cache_dir = os.path.abspath(cache_dir)
        cls._history_dir = os.path.abspath(history_dir)
        os.makedirs(cls._cache_dir, exist_ok=True)
        os.makedirs(cls._history_dir, exist_ok=True)

    @classmethod
    def set_job(cls, job_id: str):
        if not cls._cache_dir:
            raise RuntimeError("DirectoryManager.init_paths() must be called before set_job()")

        cls._job_id = job_id
        cls._run_dir = os.path.join(cls._cache_dir, job_id)
        os.makedirs(cls._run_dir, exist_ok=True)
        os.makedirs(cls.get_cache_dir(), exist_ok=True)
        os.makedirs(cls.get_videos_dir(), exist_ok=True)
        os.makedirs(cls.get_plots_root(), exist_ok=True)

    @classmethod
    def get_job_id(cls) -> Optional[str]:
        return cls._job_id

    @classmethod
    def get_run_dir(cls) -> Optional[str]:
        return cls._run_dir

    @classmethod
    def get_cache_dir(cls) -> Optional[str]:
        return os.path.join(cls._run_dir, "cache") if cls._run_dir else None

    @classmethod
    def get_videos_dir(cls) -> Optional[str]:
        return os.path.join(cls._run_dir, "videos") if cls._run_dir else None

    @classmethod
    def get_plots_root(cls) -> Optional[str]:
        return os.path.join(cls._run_dir, "plots") if cls._run_dir else None

    @classmethod
    def get_annotated_video_path(cls) -> Optional[str]:
        return os.path.join(cls.get_videos_dir(), "combined.mp4") if cls._run_dir else None

    @classmethod
    def get_joint_plot_dir(cls, joint_name: str) -> Optional[str]:
        root = cls.get_plots_root()
        if root:
            path = os.path.join(root, joint_name)
            os.makedirs(path, exist_ok=True)
            return path
        return None

    @classmethod
    def get_joint_plot_path(cls, joint_name: str, plot_name: str) -> Optional[str]:
        dir_path = cls.get_joint_plot_dir(joint_name)
        return os.path.join(dir_path, plot_name) if dir_path else None

    @classmethod
    def set_joint_plot(cls, joint_name: str, plot_name: str, plot_func):
        path = cls.get_joint_plot_path(joint_name, plot_name)
        if path:
            plot_func(path)

    @classmethod
    def set_metadata(cls, metadata: dict):
        if cls._run_dir:
            with open(os.path.join(cls._run_dir, "metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)

    @classmethod
    def get_metadata(cls) -> Optional[dict]:
        if cls._run_dir:
            path = os.path.join(cls._run_dir, "metadata.json")
            if os.path.exists(path):
                with open(path, "r") as f:
                    return json.load(f)
        return None

    @classmethod
    def set_feedback_text(cls, feedback: str):
        if cls._run_dir:
            with open(os.path.join(cls._run_dir, "llm_feedback.txt"), "w") as f:
                f.write(feedback)

    @classmethod
    def get_feedback_text(cls) -> Optional[str]:
        if cls._run_dir:
            path = os.path.join(cls._run_dir, "llm_feedback.txt")
            if os.path.exists(path):
                with open(path, "r") as f:
                    return f.read()
        return None

    @classmethod
    def save_to_history(cls, run_name: str, overwrite: bool = False) -> bool:
        if not cls._run_dir or not cls._history_dir:
            print("❌ No run or history dir set")
            return False

        print(f"📁 Saving to history: {run_name}")
        print(f"📂 Copying from: {cls._run_dir}")
        print(f"📂 Copying to: {cls._history_dir}")

        target_path = os.path.join(cls._history_dir, run_name)

        if os.path.exists(target_path):
            if not overwrite:
                print("⚠️ Run already exists and overwrite is False")
                return False
            print("⚠️ Overwriting existing history run")
            shutil.rmtree(target_path)

        shutil.copytree(cls._run_dir, target_path)

        print(f"🧹 Removing cached run at {cls._run_dir}")
        shutil.rmtree(cls._run_dir, ignore_errors=True)

        cls._job_id = None
        cls._run_dir = None

        return True

