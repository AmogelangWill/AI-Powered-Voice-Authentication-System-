import numpy as np

from app.services.features import extract_feature_vector


def test_feature_vector_shape():
    sr = 16000
    x = np.random.randn(sr * 3).astype(np.float32)
    vec = extract_feature_vector(x, sr)
    assert vec.ndim == 1
    assert vec.shape[0] > 0
