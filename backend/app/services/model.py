import pickle
from pathlib import Path

import numpy as np
from sklearn.mixture import GaussianMixture


# TODO: Advanced mode can use pretrained speaker embeddings (ECAPA-TDNN/resemblyzer).

def train_gmm(feature_matrix: np.ndarray, n_components: int = 16) -> GaussianMixture:
    if feature_matrix.ndim != 2 or feature_matrix.shape[0] < 2:
        raise ValueError("Insufficient feature data for model training")
    components = max(1, min(n_components, feature_matrix.shape[0]))
    model = GaussianMixture(n_components=components, covariance_type="diag", random_state=42)
    model.fit(feature_matrix)
    return model


def score_gmm(model: GaussianMixture, feature_matrix: np.ndarray) -> float:
    scores = model.score_samples(feature_matrix)
    return float(np.mean(scores))


def get_model_path(storage_path: str, user_id: int) -> Path:
    path = Path(storage_path)
    path.mkdir(parents=True, exist_ok=True)
    return path / f"{user_id}.pkl"


def save_gmm(model: GaussianMixture, model_path: Path) -> None:
    with model_path.open("wb") as f:
        pickle.dump(model, f)


def load_gmm(model_path: Path) -> GaussianMixture:
    with model_path.open("rb") as f:
        return pickle.load(f)
