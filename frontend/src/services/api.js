import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
})

export async function registerVoice(username, audioBlob) {
  const form = new FormData()
  form.append('username', username)
  form.append('audio_file', audioBlob, 'voice.webm')
  const { data } = await api.post('/api/v1/auth/register', form)
  return data
}

export async function loginVoice(username, audioBlob) {
  const form = new FormData()
  form.append('username', username)
  form.append('audio_file', audioBlob, 'voice.webm')
  const { data } = await api.post('/api/v1/auth/login', form)
  return data
}

export async function verifyToken(token) {
  const { data } = await api.get('/api/v1/auth/verify', {
    headers: { Authorization: `Bearer ${token}` },
  })
  return data
}
