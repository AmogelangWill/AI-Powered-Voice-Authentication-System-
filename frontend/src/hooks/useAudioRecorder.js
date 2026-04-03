import { useCallback, useEffect, useRef, useState } from 'react'

export function useAudioRecorder(maxSeconds = 10) {
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const streamRef = useRef(null)
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState(null)
  const [error, setError] = useState('')
  const [seconds, setSeconds] = useState(0)

  const stopRecording = useCallback(() => {
    if (!mediaRecorderRef.current || mediaRecorderRef.current.state === 'inactive') return
    mediaRecorderRef.current.stop()
    setIsRecording(false)
  }, [])

  useEffect(() => {
    let timer
    if (isRecording) {
      timer = window.setInterval(() => {
        setSeconds((current) => {
          if (current + 1 >= maxSeconds) {
            stopRecording()
            return maxSeconds
          }
          return current + 1
        })
      }, 1000)
    }
    return () => window.clearInterval(timer)
  }, [isRecording, maxSeconds, stopRecording])

  const startRecording = useCallback(async () => {
    setError('')
    setAudioBlob(null)
    setSeconds(0)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data)
      }
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setAudioBlob(blob)
        stream.getTracks().forEach((track) => track.stop())
      }
      mediaRecorder.start(250)
      setIsRecording(true)
    } catch (err) {
      setError('Microphone access denied or unavailable.')
      setIsRecording(false)
    }
  }, [])

  return { isRecording, startRecording, stopRecording, audioBlob, error, seconds }
}
