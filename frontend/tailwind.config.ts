import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        grama: {
          bg: "#06131F",
          card: "#0B1F2D",
          nested: "#0E2635",
          surface: "#102B3A",
          border: "#1E3A52",
          "border-subtle": "rgba(51, 65, 85, 0.6)",
          emerald: "#19D98B",
          "emerald-hover": "#16C784",
          "emerald-dark": "#0D4D33",
          cyan: "#38BDF8",
          amber: "#F59E0B",
          danger: "#EF4444",
          text: "#FFFFFF",
          muted: "#94A3B8",
          subtle: "#64748B",
        },
        brand: {
          50: "#e6fcf3",
          100: "#c2f7e0",
          200: "#8df0c3",
          300: "#4de4a2",
          400: "#19D98B",
          500: "#16C784",
          600: "#0ea86c",
          700: "#0e8557",
          800: "#106947",
          900: "#0f563c",
          950: "#063122",
        },
        surface: {
          dark: "#06131F",
          card: "#0B1F2D",
          nested: "#0E2635",
          inner: "#102B3A",
        },
      },
    },
  },
  plugins: [],
};

export default config;

