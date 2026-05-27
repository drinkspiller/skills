# Design Tokens Deep Dive

## Overview

Design tokens are the atomic values of a design system - the smallest pieces
that define visual style. They bridge the gap between design and development by
providing a single source of truth for colors, typography, spacing, and other
design decisions.

## Token Categories

### Color Tokens

```json
{
  "color": {
    "primitive": {
      "gray": {
        "0": { "value": "#ffffff" },
        "50": { "value": "#fafafa" },
        "100": { "value": "#f5f5f5" },
        "200": { "value": "#e5e5e5" },
        "300": { "value": "#d4d4d4" },
        "400": { "value": "#a3a3a3" },
        "500": { "value": "#737373" },
        "600": { "value": "#525252" },
        "700": { "value": "#404040" },
        "800": { "value": "#262626" },
        "900": { "value": "#171717" },
        "950": { "value": "#0a0a0a" }
      },
      "blue": {
        "50": { "value": "#eff6ff" },
        "100": { "value": "#dbeafe" },
        "200": { "value": "#bfdbfe" },
        "300": { "value": "#93c5fd" },
        "400": { "value": "#60a5fa" },
        "500": { "value": "#3b82f6" },
        "600": { "value": "#2563eb" },
        "700": { "value": "#1d4ed8" },
        "800": { "value": "#1e40af" },
        "900": { "value": "#1e3a8a" }
      },
      "red": {
        "500": { "value": "#ef4444" },
        "600": { "value": "#dc2626" }
      },
      "green": {
        "500": { "value": "#22c55e" },
        "600": { "value": "#16a34a" }
      },
      "amber": {
        "500": { "value": "#f59e0b" },
        "600": { "value": "#d97706" }
      }
    }
  }
}
```

### Typography Tokens

```json
{
  "typography": {
    "fontFamily": {
      "sans": { "value": "Inter, system-ui, sans-serif" },
      "mono": { "value": "JetBrains Mono, Menlo, monospace" }
    },
    "fontSize": {
      "xs": { "value": "0.75rem" },
      "sm": { "value": "0.875rem" },
      "base": { "value": "1rem" },
      "lg": { "value": "1.125rem" },
      "xl": { "value": "1.25rem" },
      "2xl": { "value": "1.5rem" },
      "3xl": { "value": "1.875rem" },
      "4xl": { "value": "2.25rem" }
    },
    "fontWeight": {
      "normal": { "value": "400" },
      "medium": { "value": "500" },
      "semibold": { "value": "600" },
      "bold": { "value": "700" }
    },
    "lineHeight": {
      "tight": { "value": "1.25" },
      "normal": { "value": "1.5" },
      "relaxed": { "value": "1.75" }
    },
    "letterSpacing": {
      "tight": { "value": "-0.025em" },
      "normal": { "value": "0" },
      "wide": { "value": "0.025em" }
    }
  }
}
```

### Spacing Tokens

```json
{
  "spacing": {
    "0": { "value": "0" },
    "0.5": { "value": "0.125rem" },
    "1": { "value": "0.25rem" },
    "1.5": { "value": "0.375rem" },
    "2": { "value": "0.5rem" },
    "2.5": { "value": "0.625rem" },
    "3": { "value": "0.75rem" },
    "3.5": { "value": "0.875rem" },
    "4": { "value": "1rem" },
    "5": { "value": "1.25rem" },
    "6": { "value": "1.5rem" },
    "7": { "value": "1.75rem" },
    "8": { "value": "2rem" },
    "9": { "value": "2.25rem" },
    "10": { "value": "2.5rem" },
    "12": { "value": "3rem" },
    "16": { "value": "4rem" },
    "20": { "value": "5rem" },
    "24": { "value": "6rem" }
  }
}
```

### Shadow Tokens

```json
{
  "shadow": {
    "xs": { "value": "0 1px 2px 0 rgb(0 0 0 / 0.05)" },
    "sm": {
      "value": "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)"
    },
    "md": {
      "value": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)"
    },
    "lg": {
      "value": "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)"
    },
    "xl": {
      "value": "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)"
    }
  }
}
```

## Token Naming Conventions

| Category  | Convention     | Example                     |
| --------- | -------------- | --------------------------- |
| Primitive  | `{category}-{scale}` | `color-blue-500`, `space-4` |
| Semantic   | `{role}-{property}`  | `text-primary`, `surface-elevated` |
| Component  | `{component}-{property}` | `button-bg`, `card-border` |

## Multi-Platform Token Generation

Tokens defined in JSON can be transformed for multiple platforms using
tools like Style Dictionary:

| Platform | Output                    |
| -------- | ------------------------- |
| Web      | CSS custom properties     |
| iOS      | Swift enums / UIColor     |
| Android  | XML resources / Compose   |
| React    | TypeScript constants      |
