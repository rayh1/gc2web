/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"],
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
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            a: {
              color: theme("colors.link"),
            },
          },
        },
      }),
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
