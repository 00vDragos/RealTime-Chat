import { GalleryVerticalEnd } from "lucide-react"
import { LoginForm } from "@/components/login-form"

export default function LoginPage() {
  return (
    <div className="bg-[rgb(var(--background))] flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="flex w-full max-w-sm flex-col gap-6 bg-[rgb(var(--card))] text-[rgb(var(--card-foreground))] rounded-xl shadow-lg p-8">
        <a href="#" className="flex items-center gap-2 self-center font-medium text-[rgb(var(--foreground))]">
          <div className="bg-[rgb(var(--primary))] text-[rgb(var(--primary-foreground))] flex size-6 items-center justify-center rounded-md">
            <GalleryVerticalEnd className="size-4" />
          </div>
          Real Time Chat
        </a>
        <LoginForm />
      </div>
    </div>
  )
}
