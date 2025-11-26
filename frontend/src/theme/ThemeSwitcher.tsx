import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { useTheme } from "./useTheme";

export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();

  const handleThemeChange = (value: string) => {
    setTheme(value as any);
    window.location.reload();
  };

  return (
    <Select value={theme} onValueChange={handleThemeChange}>
      <SelectTrigger className="w-44 h-9 text-sm">
        <SelectValue placeholder="Theme" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="endava-light">Endava Light</SelectItem>
        <SelectItem value="endava-dark">Endava Dark</SelectItem>
      </SelectContent>
    </Select>
  );
}
