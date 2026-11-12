"""Train placement readiness machine learning model with real evaluation metrics."""
import os
import sys
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from prediction.preprocessing import FEATURE_COLUMNS, LEVEL_MAPPING
from prediction.model_utils import save_model

DATASET_PATH = BASE_DIR / "prediction" / "campus_placement_dataset.csv"
MODEL_PATH = BASE_DIR / "prediction" / "trained_model.joblib"
PREPROCESSOR_PATH = BASE_DIR / "prediction" / "preprocessor.joblib"

def generate_sample_dataset(csv_path: Path, n_samples: int = 500) -> None:
    """Generate a realistic synthetic historical dataset for initial demonstration/training."""
    np.random.seed(42)
    print(f"[*] Generating synthetic training dataset with {n_samples} historical student samples at {csv_path}...")
    
    records = []
    for i in range(n_samples):
        tenth = np.clip(np.random.normal(78, 10), 50, 98)
        twelfth = np.clip(np.random.normal(76, 11), 50, 98)
        cgpa = np.clip(np.random.normal(7.4, 1.1), 5.0, 9.9)
        backlogs = np.random.choice([0, 1, 2, 3], p=[0.72, 0.18, 0.07, 0.03])
        attendance = np.clip(np.random.normal(84, 8), 60, 99)
        comm = np.random.choice([1, 2, 3], p=[0.25, 0.50, 0.25])
        apt = np.random.choice([1, 2, 3], p=[0.25, 0.50, 0.25])
        internships = np.random.choice([0, 1, 2, 3], p=[0.55, 0.32, 0.10, 0.03])
        projects = np.random.choice([0, 1, 2, 3, 4], p=[0.10, 0.35, 0.35, 0.15, 0.05])
        certs = np.random.choice([0, 1, 2], p=[0.45, 0.40, 0.15])
        skills = np.random.choice([1, 2, 3, 4, 5, 6, 7], p=[0.10, 0.15, 0.25, 0.25, 0.15, 0.07, 0.03])

        # Logical ground truth placement probability
        z = (
            (cgpa - 7.0) * 1.5
            - (backlogs * 1.8)
            + ((tenth - 70) * 0.03)
            + ((twelfth - 70) * 0.03)
            + ((comm - 2) * 0.8)
            + ((apt - 2) * 0.8)
            + (internships * 1.2)
            + (projects * 0.6)
            + (skills * 0.4)
            + (certs * 0.5)
            + ((attendance - 75) * 0.04)
        )
        prob = 1.0 / (1.0 + np.exp(-z))
        placed = 1 if np.random.rand() < prob else 0

        records.append({
            "student_id": f"HIST{1000 + i}",
            "tenth_percentage": round(tenth, 2),
            "twelfth_percentage": round(twelfth, 2),
            "cgpa": round(cgpa, 2),
            "backlogs": backlogs,
            "attendance_percentage": round(attendance, 1),
            "communication_score": comm,
            "aptitude_score": apt,
            "internship_count": internships,
            "project_count": projects,
            "certification_count": certs,
            "skill_count": skills,
            "placement_status": placed
        })

    df = pd.DataFrame(records)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    print(f"[+] Saved dataset with shape {df.shape} to {csv_path}")

def train_placement_model(csv_path=None, test_size=0.2, random_state=42):
    """
    Train Random Forest classifier on dataset.
    Fits preprocessing scaler strictly on training split to prevent data leakage.
    Evaluates real metrics and saves artifacts.
    """
    csv_file = Path(csv_path) if csv_path else DATASET_PATH
    if not csv_file.exists():
        generate_sample_dataset(csv_file)

    print(f"[*] Loading training data from {csv_file}...")
    df = pd.read_csv(csv_file)

    # Missing value handling
    for col in FEATURE_COLUMNS:
        if col in df.columns and df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    # Ensure target column exists
    target_col = "placement_status"
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataset. Columns: {list(df.columns)}")

    X = df[FEATURE_COLUMNS]
    y = df[target_col].astype(int)

    print(f"[*] Total dataset size: {len(df)} samples. Class distribution:\n{y.value_counts()}")

    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Fit Scaler strictly on train set (preventing data leakage)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train Random Forest Model
    print("[*] Training RandomForestClassifier (n_estimators=100, max_depth=6)...")
    model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=random_state)
    model.fit(X_train_scaled, y_train)

    # Evaluate on unseen test split
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    print("=" * 60)
    print("MODEL EVALUATION RESULTS (Unseen Test Set)")
    print("=" * 60)
    print(f"Accuracy : {acc:.4f} ({acc*100:.2f}%)")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1-Score : {f1:.4f}")
    print(f"Confusion Matrix:\n{cm}")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    print("=" * 60)

    # Save artifacts
    save_model(model, MODEL_PATH)
    save_model(scaler, PREPROCESSOR_PATH)
    print(f"[+] Saved trained model to {MODEL_PATH}")
    print(f"[+] Saved preprocessor scaler to {PREPROCESSOR_PATH}")

    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "confusion_matrix": cm.tolist()
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Campus Placement ML Model")
    parser.add_argument("--csv", type=str, default=None, help="Path to training CSV file")
    args = parser.parse_args()
    train_placement_model(args.csv)
