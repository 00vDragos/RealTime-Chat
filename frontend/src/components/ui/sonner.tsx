import {
  CircleCheckIcon,
  InfoIcon,
  Loader2Icon,
  OctagonXIcon,
  TriangleAlertIcon,
} from "lucide-react"
import { useTheme } from "next-themes"
import { Toaster as Sonner, type ToasterProps } from "sonner"

const Toaster = ({ ...props }: ToasterProps) => {
  const { theme = "system" } = useTheme();

  //CSS variables are defined in your index.css for Endava themes
  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      className="toaster group"
      icons={{
        success: <CircleCheckIcon className="size-4" />,
        info: <InfoIcon className="size-4" />,
        warning: <TriangleAlertIcon className="size-4" />,
        error: <OctagonXIcon className="size-4" />,
        loading: <Loader2Icon className="size-4 animate-spin" />,
      }}
      style={{
        // Use Endava theme variables for notification backgrounds, text, and borders
        '--normal-bg': 'rgb(var(--card))',
        '--normal-text': 'rgb(var(--card-foreground))',
        '--normal-border': 'rgb(var(--border))',
        '--success-bg': 'rgb(var(--primary))',
        '--success-text': 'rgb(var(--primary-foreground))',
        '--error-bg': 'rgb(var(--destructive))',
        '--error-text': 'rgb(var(--destructive-foreground))',
        '--warning-bg': 'rgb(var(--muted))',
        '--warning-text': 'rgb(var(--muted-foreground))',
        '--info-bg': 'rgb(var(--accent))',
        '--info-text': 'rgb(var(--accent-foreground))',
        '--border-radius': 'var(--radius)',
      } as React.CSSProperties}
      {...props}
    />
  );
}

export { Toaster }
