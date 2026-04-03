export default function StatusBadge({ status, message }) {
  if (!message) return null

  const classes =
    status === 'success'
      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-400/30'
      : status === 'error'
      ? 'bg-rose-500/20 text-rose-300 border-rose-400/30'
      : 'bg-slate-500/20 text-slate-300 border-slate-400/30'

  return <div className={`mt-4 rounded border px-3 py-2 text-sm ${classes}`}>{message}</div>
}
