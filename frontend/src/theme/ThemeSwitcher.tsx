import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { useTheme, type Theme } from "./useTheme";

export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();

  return (
    
    <Select value={theme} onValueChange={v => setTheme(v as Theme)}>
      <SelectTrigger className="w-40">
        <SelectValue />
      </SelectTrigger>

      <SelectContent>
        <SelectItem value="light">Light</SelectItem>
        <SelectItem value="dark">Dark</SelectItem>
        <SelectItem value="forest">Forest</SelectItem>
        <SelectItem value="sunrise">Sunrise</SelectItem>
      </SelectContent>
    </Select>
  );
}
