def test_register_and_login_flow(client, sine_wave_wav_bytes):
    register_response = client.post(
        "/api/v1/auth/register",
        data={"username": "alice"},
        files={"audio_file": ("voice.wav", sine_wave_wav_bytes, "audio/wav")},
    )
    assert register_response.status_code == 200
    assert register_response.json()["message"] == "Voice registered successfully"

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "alice"},
        files={"audio_file": ("voice.wav", sine_wave_wav_bytes, "audio/wav")},
    )
    assert login_response.status_code == 200
    body = login_response.json()
    assert "access_token" in body
    assert "refresh_token" in body

    verify_response = client.get(
        "/api/v1/auth/verify",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["verified"] is True
