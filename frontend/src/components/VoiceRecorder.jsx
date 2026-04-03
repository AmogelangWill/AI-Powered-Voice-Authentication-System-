import { useEffect, useRef } from 'react'

export default function VoiceRecorder({
  isRecording,
  startRecording,
  stopRecording,
  audioBlob,
  seconds,
}) {
  const canvasRef = useRef(null)
  const animationRef = useRef(null)

  useEffect(() => {
    if (!isRecording || !canvasRef.current) return
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      for (let x = 0; x < canvas.width; x += 8) {
        const bar = Math.random() * canvas.height
        ctx.fillStyle = '#38bdf8'
        ctx.fillRect(x, canvas.height - bar, 5, bar)
      }
      animationRef.current = requestAnimationFrame(draw)
    }

    draw()
    return () => cancelAnimationFrame(animationRef.current)
  }, [isRecording])

  return (
    <div className="rounded-lg border border-slate-700 p-4">
      <div className="mb-3 flex items-center gap-3">
        {!isRecording ? (
          <button
            className="rounded bg-sky-500 px-4 py-2 font-medium text-white"
            onClick={startRecording}
          >
            Start Recording
          </button>
        ) : (
          <button
            className="rounded bg-rose-500 px-4 py-2 font-medium text-white"
            onClick={stopRecording}
          >
            Stop Recording
          </button>
        )}
        <span className="text-sm text-slate-300">Timer: {seconds}s</span>
      </div>

      <canvas ref={canvasRef} width={480} height={100} className="w-full rounded bg-slate-950" />

      {audioBlob && (
        <audio
          className="mt-3 w-full"
          controls
          src={URL.createObjectURL(audioBlob)}
        />
      )}
    </div>
  )
}
