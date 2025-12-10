import { useState } from "react"
import { GalleryVerticalEnd } from "lucide-react"
import { LoginForm } from "@/components/login-form"
import { RegisterForm } from "@/components/register-form"

export default function LoginPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login')

  return (
    <div className="bg-[rgb(var(--background))] flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="flex w-full max-w-sm flex-col gap-6 bg-[rgb(var(--card))] text-[rgb(var(--card-foreground))] rounded-xl shadow-lg p-8">
        <a href="#" className="flex items-center gap-2 self-center font-medium text-[rgb(var(--foreground))]">
          <div className="bg-[rgb(var(--primary))] text-[rgb(var(--primary-foreground))] flex size-6 items-center justify-center rounded-md">
            <GalleryVerticalEnd className="size-4" />
          </div>
          Real Time Chat
        </a>
        <div className="grid grid-cols-2 rounded-lg border bg-[rgb(var(--muted))] p-1 text-sm font-medium">
          <button
            type="button"
            className={`h-9 rounded-md transition-colors ${mode === 'login' ? 'bg-[rgb(var(--background))] text-[rgb(var(--foreground))]' : 'text-[rgb(var(--muted-foreground))]'}`}
            onClick={() => setMode('login')}
          >
            Sign in
          </button>
          <button
            type="button"
            className={`h-9 rounded-md transition-colors ${mode === 'register' ? 'bg-[rgb(var(--background))] text-[rgb(var(--foreground))]' : 'text-[rgb(var(--muted-foreground))]'}`}
            onClick={() => setMode('register')}
          >
            Create account
          </button>
        </div>

        {mode === 'login' ? <LoginForm /> : <RegisterForm />}
      </div>
    </div>
  )
}
