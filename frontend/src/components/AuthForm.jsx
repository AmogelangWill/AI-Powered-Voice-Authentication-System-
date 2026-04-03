import { useState } from 'react'

import { loginVoice, registerVoice, verifyToken } from '../services/api'
import StatusBadge from './StatusBadge'
import VoiceRecorder from './VoiceRecorder'
import { useAudioRecorder } from '../hooks/useAudioRecorder'

export default function AuthForm() {
  const [mode, setMode] = useState('register')
  const [username, setUsername] = useState('')
  const [status, setStatus] = useState('info')
  const [message, setMessage] = useState('')
  const [token, setToken] = useState('')

  const { isRecording, startRecording, stopRecording, audioBlob, error, seconds } = useAudioRecorder()

  const submit = async (event) => {
    event.preventDefault()
    setMessage('')
    if (!username || !audioBlob) {
      setStatus('error')
      setMessage('Please provide a username and a recording.')
      return
    }

    try {
      if (mode === 'register') {
        const result = await registerVoice(username, audioBlob)
        setStatus('success')
        setMessage(result.message)
      } else {
        const result = await loginVoice(username, audioBlob)
        setToken(result.access_token)
        const verified = await verifyToken(result.access_token)
        setStatus('success')
        setMessage(`Login successful for user ${verified.user_id}`)
      }
    } catch (apiError) {
      setStatus('error')
      setMessage(apiError?.response?.data?.detail || 'Request failed.')
    }
  }

  return (
    <form onSubmit={submit} className="mx-auto mt-10 max-w-xl rounded-lg border border-slate-700 p-6">
      <div className="mb-4 flex gap-2">
        <button
          type="button"
          className={`rounded px-3 py-2 ${mode === 'register' ? 'bg-sky-600' : 'bg-slate-700'}`}
          onClick={() => setMode('register')}
        >
          Register
        </button>
        <button
          type="button"
          className={`rounded px-3 py-2 ${mode === 'login' ? 'bg-sky-600' : 'bg-slate-700'}`}
          onClick={() => setMode('login')}
        >
          Login
        </button>
      </div>

      <label className="mb-3 block text-sm">Username</label>
      <input
        className="mb-4 w-full rounded border border-slate-600 bg-slate-800 px-3 py-2"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Enter username"
      />

      <VoiceRecorder
        isRecording={isRecording}
        startRecording={startRecording}
        stopRecording={stopRecording}
        audioBlob={audioBlob}
        seconds={seconds}
      />

      <button
        type="submit"
        disabled={!audioBlob || isRecording}
        className="mt-4 rounded bg-emerald-600 px-4 py-2 disabled:opacity-50"
      >
        Submit {mode === 'register' ? 'Registration' : 'Login'}
      </button>

      {error && <StatusBadge status="error" message={error} />}
      {token && <div className="mt-2 text-xs break-all">Access token: {token}</div>}
      <StatusBadge status={status} message={message} />
    </form>
  )
}
