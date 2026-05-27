# Theming Architecture

## Overview

A robust theming system enables applications to support multiple visual
appearances (light/dark modes, brand themes) while maintaining consistency and
developer experience.

## CSS Custom Properties Architecture

### Base Setup

```css
/* 1. Define the token contract */
:root {
  /* Color scheme */
  color-scheme: light dark;

  /* Base tokens that don't change */
  --font-sans: Inter, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;

  /* Animation tokens */
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);

  /* Z-index scale */
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-modal: 300;
  --z-popover: 400;
  --z-tooltip: 500;
}

/* 2. Light theme (default) */
:root,
[data-theme="light"] {
  --color-bg: #ffffff;
  --color-bg-subtle: #f8fafc;
  --color-bg-muted: #f1f5f9;
  --color-bg-emphasis: #0f172a;

  --color-text: #0f172a;
  --color-text-muted: #475569;
  --color-text-subtle: #94a3b8;

  --color-border: #e2e8f0;
  --color-border-muted: #f1f5f9;

  --color-accent: #3b82f6;
  --color-accent-hover: #2563eb;
  --color-accent-muted: #dbeafe;

  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}

/* 3. Dark theme */
[data-theme="dark"] {
  --color-bg: #0f172a;
  --color-bg-subtle: #1e293b;
  --color-bg-muted: #334155;
  --color-bg-emphasis: #f8fafc;

  --color-text: #f8fafc;
  --color-text-muted: #94a3b8;
  --color-text-subtle: #64748b;

  --color-border: #334155;
  --color-border-muted: #1e293b;

  --color-accent: #60a5fa;
  --color-accent-hover: #93c5fd;
  --color-accent-muted: #1e3a5f;

  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.4);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.5);
}

/* 4. System preference detection */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    /* Inherit dark theme values */
    --color-bg: #0f172a;
    --color-bg-subtle: #1e293b;
    --color-bg-muted: #334155;
    --color-bg-emphasis: #f8fafc;
    --color-text: #f8fafc;
    --color-text-muted: #94a3b8;
    --color-text-subtle: #64748b;
    --color-border: #334155;
    --color-border-muted: #1e293b;
    --color-accent: #60a5fa;
    --color-accent-hover: #93c5fd;
    --color-accent-muted: #1e3a5f;
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.4);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.5);
  }
}
```

### Using Tokens in Components

```css
.card {
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  box-shadow: var(--shadow-sm);
  padding: 1.5rem;
}

.card-title {
  color: var(--color-text);
  font-family: var(--font-sans);
  font-size: 1.125rem;
  font-weight: 600;
}

.card-description {
  color: var(--color-text-muted);
  margin-top: 0.5rem;
}

.button-primary {
  background: var(--color-accent);
  color: white;
  transition: background var(--duration-fast) var(--ease-default);
}

.button-primary:hover {
  background: var(--color-accent-hover);
}
```

## React Theme Provider

### Complete Implementation

```tsx
// theme-provider.tsx
import * as React from "react";

type Theme = "light" | "dark" | "system";
type ResolvedTheme = "light" | "dark";

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
  attribute?: "class" | "data-theme";
  enableSystem?: boolean;
  disableTransitionOnChange?: boolean;
}

interface ThemeProviderState {
  theme: Theme;
  resolvedTheme: ResolvedTheme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

const ThemeProviderContext = React.createContext<
  ThemeProviderState | undefined
>(undefined);

export function ThemeProvider({
  children,
  defaultTheme = "system",
  storageKey = "theme",
  attribute = "data-theme",
  enableSystem = true,
  disableTransitionOnChange = false,
}: ThemeProviderProps) {
  const [theme, setThemeState] = React.useState<Theme>(() => {
    if (typeof window === "undefined") return defaultTheme;
    return (localStorage.getItem(storageKey) as Theme) || defaultTheme;
  });

  const [resolvedTheme, setResolvedTheme] =
    React.useState<ResolvedTheme>("light");

  // Get system preference
  const getSystemTheme = React.useCallback((): ResolvedTheme => {
    if (typeof window === "undefined") return "light";
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }, []);

  // Apply theme to DOM
  React.useEffect(() => {
    const root = document.documentElement;
    const resolved = theme === "system" ? getSystemTheme() : theme;

    // Disable transitions during theme change
    if (disableTransitionOnChange) {
      root.style.setProperty("transition", "none");
      requestAnimationFrame(() => {
        root.style.removeProperty("transition");
      });
    }

    if (attribute === "class") {
      root.classList.remove("light", "dark");
      root.classList.add(resolved);
    } else {
      root.setAttribute(attribute, resolved);
    }

    setResolvedTheme(resolved);
  }, [theme, attribute, disableTransitionOnChange, getSystemTheme]);

  // Watch system theme changes
  React.useEffect(() => {
    if (!enableSystem || theme !== "system") return;

    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => {
      const resolved = getSystemTheme();
      setResolvedTheme(resolved);
      document.documentElement.setAttribute(attribute, resolved);
    };

    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, [enableSystem, theme, attribute, getSystemTheme]);

  const setTheme = React.useCallback(
    (newTheme: Theme) => {
      setThemeState(newTheme);
      localStorage.setItem(storageKey, newTheme);
    },
    [storageKey],
  );

  const toggleTheme = React.useCallback(() => {
    setTheme(resolvedTheme === "light" ? "dark" : "light");
  }, [resolvedTheme, setTheme]);

  return (
    <ThemeProviderContext.Provider
      value={{ theme, resolvedTheme, setTheme, toggleTheme }}
    >
      {children}
    </ThemeProviderContext.Provider>
  );
}

export function useTheme() {
  const context = React.useContext(ThemeProviderContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}
```

## Multi-Brand Theming

For applications that need to support multiple brands:

```css
/* Brand A */
[data-brand="brand-a"] {
  --color-accent: #3b82f6;
  --color-accent-hover: #2563eb;
  --font-sans: "Inter", system-ui, sans-serif;
  --radius-default: 0.5rem;
}

/* Brand B */
[data-brand="brand-b"] {
  --color-accent: #8b5cf6;
  --color-accent-hover: #7c3aed;
  --font-sans: "Poppins", system-ui, sans-serif;
  --radius-default: 1rem;
}

/* Brand C */
[data-brand="brand-c"] {
  --color-accent: #06b6d4;
  --color-accent-hover: #0891b2;
  --font-sans: "DM Sans", system-ui, sans-serif;
  --radius-default: 0;
}
```

## Accessibility Considerations

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  :root {
    --duration-fast: 0ms;
    --duration-normal: 0ms;
    --duration-slow: 0ms;
  }
}
```

### High Contrast

```css
@media (prefers-contrast: high) {
  :root {
    --color-border: #000000;
    --color-text: #000000;
    --color-bg: #ffffff;
  }

  [data-theme="dark"] {
    --color-border: #ffffff;
    --color-text: #ffffff;
    --color-bg: #000000;
  }
}
```
