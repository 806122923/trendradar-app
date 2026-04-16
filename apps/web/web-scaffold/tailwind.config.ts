import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "muted-foreground": "hsl(215 16% 47%)",
      },
    },
  },
  plugins: [],
};

export default config;
