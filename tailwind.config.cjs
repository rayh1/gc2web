/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        header: "#fff",
        "header-foreground": "#000",
        link: "#2563EB",
        primary: {
          500: "#2563EB",
          600: "#1D4ED8",
        },
        "primary-foreground": "#fff",
        dark: {
          bg: "#121212",
          surface: "#1E1E1E",
          text: "#E5E5E5",
          "text-muted": "#A3A3A3"
        }
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            a: {
              color: theme("colors.link"),
            },
          },
        },
        dark: {
          css: {
            color: theme("colors.dark.text"),
            a: {
              color: theme("colors.primary.500"),
            },
            h1: { color: theme("colors.dark.text") },
            h2: { color: theme("colors.dark.text") },
            h3: { color: theme("colors.dark.text") },
            h4: { color: theme("colors.dark.text") },
            p: { color: theme("colors.dark.text") },
            strong: { color: theme("colors.dark.text") },
            blockquote: { 
              color: theme("colors.dark.text"),
              borderColor: theme("colors.primary.500"),
              backgroundColor: theme("colors.dark.surface")
            },
            code: { color: theme("colors.dark.text") },
          },
        },
      }),
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
