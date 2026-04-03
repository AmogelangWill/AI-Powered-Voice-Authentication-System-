import numpy as np
import librosa
from sklearn.preprocessing import StandardScaler


def _fix_frames(values: np.ndarray, n_frames: int) -> np.ndarray:
    return librosa.util.fix_length(values, size=n_frames, axis=1)


def extract_frame_features(y: np.ndarray, sr: int) -> np.ndarray:
    # Per-frame feature matrix used for GMM training and scoring.
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    n_frames = mfcc.shape[1]

    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=20)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    mel_db = _fix_frames(mel_db, n_frames)

    zcr = _fix_frames(librosa.feature.zero_crossing_rate(y), n_frames)
    centroid = _fix_frames(librosa.feature.spectral_centroid(y=y, sr=sr), n_frames)
    bandwidth = _fix_frames(librosa.feature.spectral_bandwidth(y=y, sr=sr), n_frames)
    rolloff = _fix_frames(librosa.feature.spectral_rolloff(y=y, sr=sr), n_frames)

    frame_matrix = np.vstack([mfcc, mel_db, zcr, centroid, bandwidth, rolloff]).T
    scaler = StandardScaler()
    return scaler.fit_transform(frame_matrix)


def extract_feature_vector(y: np.ndarray, sr: int) -> np.ndarray:
    # Aggregated 1D vector for diagnostics and test coverage.
    frame_features = extract_frame_features(y, sr)
    means = frame_features.mean(axis=0)
    stds = frame_features.std(axis=0)
    return np.concatenate([means, stds]).astype(np.float32)
