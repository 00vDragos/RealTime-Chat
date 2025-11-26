export type Theme = "light" | "dark" | "forest" | "sunrise";

import { useThemeContext } from "./ThemeProvider";

export function useTheme() {
  return useThemeContext();
}
