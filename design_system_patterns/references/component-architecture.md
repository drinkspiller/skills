# Component Architecture Patterns

## Overview

Well-architected components are reusable, composable, and maintainable. This
guide covers patterns for building flexible component APIs that scale across
design systems.

## Compound Components

Compound components share implicit state through React context, allowing
flexible composition.

```tsx
// Compound component pattern
import * as React from "react";

interface AccordionContextValue {
  openItems: Set<string>;
  toggle: (id: string) => void;
  type: "single" | "multiple";
}

const AccordionContext = React.createContext<AccordionContextValue | null>(null);

function useAccordionContext() {
  const context = React.useContext(AccordionContext);
  if (!context) {
    throw new Error("Accordion components must be used within an Accordion");
  }
  return context;
}

// Root component
interface AccordionProps {
  children: React.ReactNode;
  type?: "single" | "multiple";
  defaultOpen?: string[];
}

function Accordion({
  children,
  type = "single",
  defaultOpen = [],
}: AccordionProps) {
  const [openItems, setOpenItems] = React.useState<Set<string>>(
    new Set(defaultOpen),
  );

  const toggle = React.useCallback(
    (id: string) => {
      setOpenItems((prev) => {
        const next = new Set(prev);
        if (next.has(id)) {
          next.delete(id);
        } else {
          if (type === "single") {
            next.clear();
          }
          next.add(id);
        }
        return next;
      });
    },
    [type],
  );

  return (
    <AccordionContext.Provider value={{ openItems, toggle, type }}>
      <div className="divide-y divide-border">{children}</div>
    </AccordionContext.Provider>
  );
}

// Item component
const AccordionItemContext = React.createContext<{ id: string } | null>(null);

function useAccordionItemContext() {
  const context = React.useContext(AccordionItemContext);
  if (!context) {
    throw new Error("AccordionItem context not found");
  }
  return context;
}

interface AccordionItemProps {
  children: React.ReactNode;
  id: string;
}

function AccordionItem({ children, id }: AccordionItemProps) {
  return (
    <AccordionItemContext.Provider value={{ id }}>
      <div className="py-2">{children}</div>
    </AccordionItemContext.Provider>
  );
}

// Trigger component
function AccordionTrigger({ children }: { children: React.ReactNode }) {
  const { toggle, openItems } = useAccordionContext();
  const { id } = useAccordionItemContext();
  const isOpen = openItems.has(id);

  return (
    <button
      onClick={() => toggle(id)}
      className="flex w-full items-center justify-between py-2 font-medium"
      aria-expanded={isOpen}
    >
      {children}
      <ChevronDown
        className={`h-4 w-4 transition-transform ${isOpen ? "rotate-180" : ""}`}
      />
    </button>
  );
}

// Content component
function AccordionContent({ children }: { children: React.ReactNode }) {
  const { openItems } = useAccordionContext();
  const { id } = useAccordionItemContext();
  const isOpen = openItems.has(id);

  if (!isOpen) return null;

  return <div className="pb-4 text-muted-foreground">{children}</div>;
}

// Export compound component
export const AccordionCompound = Object.assign(Accordion, {
  Item: AccordionItem,
  Trigger: AccordionTrigger,
  Content: AccordionContent,
});

// Usage
function Example() {
  return (
    <AccordionCompound type="single" defaultOpen={["item-1"]}>
      <AccordionCompound.Item id="item-1">
        <AccordionCompound.Trigger>Is it accessible?</AccordionCompound.Trigger>
        <AccordionCompound.Content>
          Yes. It follows WAI-ARIA patterns.
        </AccordionCompound.Content>
      </AccordionCompound.Item>
      <AccordionCompound.Item id="item-2">
        <AccordionCompound.Trigger>Is it styled?</AccordionCompound.Trigger>
        <AccordionCompound.Content>
          Yes. It uses Tailwind CSS.
        </AccordionCompound.Content>
      </AccordionCompound.Item>
    </AccordionCompound>
  );
}
```

## Polymorphic Components

Polymorphic components can render as different HTML elements or other
components.

```tsx
// Polymorphic component with proper TypeScript support
import * as React from "react";

type AsProp<C extends React.ElementType> = {
  as?: C;
};

type PropsToOmit<C extends React.ElementType, P> = keyof (AsProp<C> & P);

type PolymorphicComponentProp<
  C extends React.ElementType,
  Props = {},
> = React.PropsWithChildren<Props & AsProp<C>> &
  Omit<React.ComponentPropsWithoutRef<C>, PropsToOmit<C, Props>>;

type PolymorphicRef<C extends React.ElementType> =
  React.ComponentPropsWithRef<C>["ref"];

type PolymorphicComponentPropWithRef<
  C extends React.ElementType,
  Props = {},
> = PolymorphicComponentProp<C, Props> & { ref?: PolymorphicRef<C> };

// Button component
interface ButtonOwnProps {
  variant?: "default" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
}

type ButtonProps<C extends React.ElementType = "button"> =
  PolymorphicComponentPropWithRef<C, ButtonOwnProps>;

const Button = React.forwardRef(
  <C extends React.ElementType = "button">(
    { as, variant = "default", size = "md", ...props }: ButtonProps<C>,
    ref: PolymorphicRef<C>,
  ) => {
    const Component = as || "button";
    return <Component ref={ref} {...props} />;
  },
);

// Usage
function PolymorphicExample() {
  return (
    <>
      <Button>Click me</Button>
      <Button as="a" href="/about">
        Navigate
      </Button>
      <Button as={Link} to="/dashboard">
        Route
      </Button>
    </>
  );
}
```

## Variant Systems

Use a consistent variant pattern for component APIs.

```tsx
// Simple variant map approach
const variantStyles = {
  default:
    "bg-blue-600 text-white hover:bg-blue-700 focus-visible:ring-blue-500",
  secondary:
    "bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:ring-gray-500",
  destructive:
    "bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500",
  ghost: "hover:bg-gray-100 text-gray-700 focus-visible:ring-gray-500",
  link: "text-blue-600 underline-offset-4 hover:underline p-0 h-auto",
} as const;

const sizeStyles = {
  sm: "h-8 px-3 text-sm rounded-md",
  md: "h-10 px-4 text-sm rounded-lg",
  lg: "h-12 px-6 text-base rounded-lg",
} as const;
```
