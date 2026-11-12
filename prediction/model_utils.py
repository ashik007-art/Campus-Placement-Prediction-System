"""Model persistence utilities using joblib."""
from pathlib import Path
import joblib

def model_exists(filepath: str | Path) -> bool:
    """Check if model artifact exists on disk."""
    if not filepath:
        return False
    path = Path(filepath)
    return path.exists() and path.is_file()

def save_model(artifact, filepath: str | Path) -> None:
    """Persist model or preprocessor to disk."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, path)

def load_model(filepath: str | Path):
    """Load persisted model artifact from disk."""
    path = Path(filepath)
    if not path.exists():
        return None
    try:
        return joblib.load(path)
    except Exception as e:
        print(f"[Warning] Failed to load model artifact from {filepath}: {e}")
        return None
