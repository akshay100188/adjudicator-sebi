"use client";

import { useEffect, useState } from "react";

/**
 * Light/dark theme toggle. Light is the default; the choice is persisted to
 * localStorage and applied as a `dark` class on <html>. The initial class is
 * set by an inline script in layout.tsx so there's no flash on first paint.
 */
export function ThemeToggle() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    setDark(document.documentElement.classList.contains("dark"));
  }, []);

  function toggle() {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    try {
      localStorage.theme = next ? "dark" : "light";
    } catch {
      /* ignore (e.g. private mode) */
    }
  }

  return (
    <button
      onClick={toggle}
      aria-label="Toggle dark mode"
      className="flex w-full items-center justify-center gap-2 rounded border border-slate-200 bg-white px-3 py-2 text-xs text-slate-700 hover:bg-slate-100 dark:border-slate-800 dark:bg-slate-900/60 dark:text-slate-300 dark:hover:bg-slate-800"
    >
      {dark ? "☀ Light mode" : "🌙 Dark mode"}
    </button>
  );
}
