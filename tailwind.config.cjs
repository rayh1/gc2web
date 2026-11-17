/*
 * Fonts and archive colours are constants, not theme() lookups: under Tailwind 4's
 * @config compatibility, theme() inside the typography function returns undefined.
 */
const fontFamily = {
  body: ['"IBM Plex Sans"', '"Segoe UI"', 'sans-serif'],
  display: ['"Iowan Old Style"', '"Palatino Linotype"', 'serif'],
};

const archive = {
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
};

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily,
      colors: {
        header: "#fff",
        "header-foreground": "#000",
        link: "#2563EB",
        archive,
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
      typography: {
        DEFAULT: {
          css: {
            color: archive.ink,
            fontFamily: fontFamily.body.join(", "),
            a: {
              color: archive.accent,
            },
            h1: {
              color: archive.ink,
              fontFamily: fontFamily.display.join(", "),
            },
            h2: {
              color: archive.ink,
              fontFamily: fontFamily.display.join(", "),
            },
            h3: {
              color: archive.ink,
              fontFamily: fontFamily.display.join(", "),
            },
            h4: {
              color: archive.ink,
              fontFamily: fontFamily.display.join(", "),
            },
            strong: {
              color: archive.ink,
            },
          },
        },
        dark: {
          css: {
            color: archive.dark.ink,
            a: {
              color: archive.dark.accent,
            },
            h1: { color: archive.dark.ink },
            h2: { color: archive.dark.ink },
            h3: { color: archive.dark.ink },
            h4: { color: archive.dark.ink },
            p: { color: archive.dark.ink },
            strong: { color: archive.dark.ink },
            blockquote: {
              color: archive.dark.ink,
              borderColor: archive.dark.accent,
              backgroundColor: archive.dark.paper
            },
            code: { color: archive.dark.ink },
          },
        },
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
