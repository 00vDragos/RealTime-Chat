import { memo } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface TypingIndicatorProps {
  label: string;
  avatarUrl?: string | null;
  fallbackInitial?: string;
}

function TypingIndicatorComponent({ label, avatarUrl, fallbackInitial }: TypingIndicatorProps) {
  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-2xl bg-[rgb(var(--background))] shadow text-xs text-[rgb(var(--muted-foreground))]">
      <Avatar className="h-6 w-6 border border-[rgb(var(--border))]">
        {avatarUrl && <AvatarImage src={avatarUrl} alt="Typing avatar" />}
        <AvatarFallback className="text-[0.65rem]">
          {(fallbackInitial || "").trim().charAt(0)?.toUpperCase() || "U"}
        </AvatarFallback>
      </Avatar>
      <span>{label}</span>
      <div className="flex items-end gap-1">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-[rgb(var(--muted-foreground))] animate-bounce"
            style={{ animationDelay: `${i * 150}ms` }}
          />
        ))}
      </div>
    </div>
  );
}

const TypingIndicator = memo(TypingIndicatorComponent);
TypingIndicator.displayName = "TypingIndicator";

export default TypingIndicator;
