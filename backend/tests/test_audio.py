import pytest
from fastapi import UploadFile

from app.services.audio import read_and_preprocess_audio


@pytest.mark.asyncio
async def test_audio_preprocess_success(sine_wave_wav_bytes):
    upload = UploadFile(filename="sample.wav", file=__import__("io").BytesIO(sine_wave_wav_bytes), headers={"content-type": "audio/wav"})
    upload.content_type = "audio/wav"
    y, sr = await read_and_preprocess_audio(upload, min_duration_seconds=2, max_duration_seconds=10)
    assert sr == 16000
    assert len(y) > 0


@pytest.mark.asyncio
async def test_audio_preprocess_duration_validation(short_wav_bytes):
    upload = UploadFile(filename="short.wav", file=__import__("io").BytesIO(short_wav_bytes), headers={"content-type": "audio/wav"})
    upload.content_type = "audio/wav"
    with pytest.raises(Exception):
        await read_and_preprocess_audio(upload, min_duration_seconds=2, max_duration_seconds=10)
