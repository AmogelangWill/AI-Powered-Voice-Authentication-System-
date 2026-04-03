import io
import tempfile

import librosa
import noisereduce as nr
import numpy as np
import soundfile as sf
from fastapi import HTTPException, UploadFile, status

ALLOWED_AUDIO_TYPES = {"audio/wav", "audio/webm", "audio/ogg"}
TARGET_SAMPLE_RATE = 16000


async def _read_audio_bytes(audio_file: UploadFile) -> bytes:
    data = await audio_file.read()
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio file is empty")
    return data


def _decode_audio(data: bytes) -> tuple[np.ndarray, int]:
    try:
        y, sr = sf.read(io.BytesIO(data), always_2d=False)
        y = np.asarray(y, dtype=np.float32)
        return y, int(sr)
    except Exception:
        # Fallback path for container/codec combinations unsupported by soundfile.
        with tempfile.NamedTemporaryFile(suffix=".tmp") as tmp:
            tmp.write(data)
            tmp.flush()
            y, sr = librosa.load(tmp.name, sr=None, mono=False)
            y = np.asarray(y, dtype=np.float32)
            return y, int(sr)


def _to_mono(y: np.ndarray) -> np.ndarray:
    if y.ndim == 1:
        return y
    return np.mean(y, axis=1 if y.shape[0] > y.shape[1] else 0)


def _normalize_audio(y: np.ndarray) -> np.ndarray:
    peak = float(np.max(np.abs(y)))
    if peak <= 0:
        return y
    return y / peak


async def read_and_preprocess_audio(
    audio_file: UploadFile,
    min_duration_seconds: int,
    max_duration_seconds: int,
) -> tuple[np.ndarray, int]:
    if audio_file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported audio format")

    data = await _read_audio_bytes(audio_file)
    y, sr = _decode_audio(data)
    y = _to_mono(y)

    if sr != TARGET_SAMPLE_RATE:
        y = librosa.resample(y, orig_sr=sr, target_sr=TARGET_SAMPLE_RATE)
        sr = TARGET_SAMPLE_RATE

    duration = float(len(y) / sr)
    if duration < min_duration_seconds or duration > max_duration_seconds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Audio duration must be between {min_duration_seconds} and {max_duration_seconds} seconds",
        )

    y = _normalize_audio(y)
    y = nr.reduce_noise(y=y, sr=sr)
    return y.astype(np.float32), sr
