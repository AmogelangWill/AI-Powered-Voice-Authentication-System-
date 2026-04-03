import AuthForm from './components/AuthForm'

export default function App() {
  return (
    <main className="p-6">
      <h1 className="text-center text-3xl font-semibold">Voiceprint Authentication</h1>
      <p className="mt-2 text-center text-slate-300">Register and login with your voice.</p>
      <AuthForm />
    </main>
  )
}
