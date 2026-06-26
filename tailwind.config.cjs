/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        body: ['"IBM Plex Sans"', '"Segoe UI"', 'sans-serif'],
        display: ['"Iowan Old Style"', '"Palatino Linotype"', 'serif'],
      },
      colors: {
        header: "#fff",
        "header-foreground": "#000",
        link: "#2563EB",
        archive: {
          canvas: "#f3ece2",
          paper: "#fff9f1",
          ink: "#2f241d",
          muted: "#6c5a4f",
          accent: "#9d5b33",
          line: "#dbc9b8",
          dark: {
            canvas: "#171210",
            paper: "#241c18",
            ink: "#f2e5d6",
            muted: "#bea894",
            accent: "#e39a59",
            line: "#4a3a31",
          },
        },
        primary: {
          300: "#93C5FD",  // Adding lighter shade for dark mode hover
          400: "#60A5FA",
          500: "#2563EB",
          600: "#1D4ED8",
          700: "#1E40AF"   // Adding darker shade for hover
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
            color: theme("colors.archive.ink"),
            fontFamily: theme("fontFamily.body").join(", "),
            a: {
              color: theme("colors.archive.accent"),
            },
            h1: {
              color: theme("colors.archive.ink"),
              fontFamily: theme("fontFamily.display").join(", "),
            },
            h2: {
              color: theme("colors.archive.ink"),
              fontFamily: theme("fontFamily.display").join(", "),
            },
            h3: {
              color: theme("colors.archive.ink"),
              fontFamily: theme("fontFamily.display").join(", "),
            },
            h4: {
              color: theme("colors.archive.ink"),
              fontFamily: theme("fontFamily.display").join(", "),
            },
            strong: {
              color: theme("colors.archive.ink"),
            },
          },
        },
        dark: {
          css: {
            color: theme("colors.archive.dark.ink"),
            a: {
              color: theme("colors.archive.dark.accent"),
            },
            h1: { color: theme("colors.archive.dark.ink") },
            h2: { color: theme("colors.archive.dark.ink") },
            h3: { color: theme("colors.archive.dark.ink") },
            h4: { color: theme("colors.archive.dark.ink") },
            p: { color: theme("colors.archive.dark.ink") },
            strong: { color: theme("colors.archive.dark.ink") },
            blockquote: {
              color: theme("colors.archive.dark.ink"),
              borderColor: theme("colors.archive.dark.accent"),
              backgroundColor: theme("colors.archive.dark.paper")
            },
            code: { color: theme("colors.archive.dark.ink") },
          },
        },
      }),
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
