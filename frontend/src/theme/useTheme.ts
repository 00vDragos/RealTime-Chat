// src/theme/useTheme.ts
import { useEffect, useState } from "react";

export type Theme = "endava-light" | "endava-dark";

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    return (localStorage.getItem("theme") as Theme) || "endava-light";
  });

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("theme-endava-light", "theme-endava-dark");
    if (theme === "endava-dark") {
      root.classList.add("theme-endava-dark");
    } else {
      root.classList.add("theme-endava-light");
    }
    localStorage.setItem("theme", theme);
  }, [theme]);

  return { theme, setTheme };
}
