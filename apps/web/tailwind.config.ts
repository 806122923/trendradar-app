import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Mirror landing.html's design tokens
        acid: {
          DEFAULT: "#FF4F1A",
          deep: "#D93E0E",
        },
        ink: "#000000",
        paper: "#ffffff",
        line: "#e5e5e5",
        muted: "#8a8a8a",
        pos: "#00C853",
        "muted-foreground": "hsl(215 16% 47%)",
      },
      fontFamily: {
        // Populated by `next/font/google` CSS variables in layout.tsx
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        sans: [
          "var(--font-sans)",
          "PingFang SC",
          "Microsoft YaHei",
          "system-ui",
          "sans-serif",
        ],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      borderRadius: {
        // Landing uses 2px corners; keep Tailwind's `rounded-sm` aligned
        sm: "2px",
      },
      letterSpacing: {
        label: "0.14em",
      },
    },
  },
  plugins: [],
};

export default config;
