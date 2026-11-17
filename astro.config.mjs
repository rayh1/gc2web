import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";
import solidJs from "@astrojs/solid-js";
import tailwindcss from "@tailwindcss/vite";
import { SITE_URL } from "./src/consts.ts";
import remarkGemoji from 'remark-gemoji'

// https://astro.build/config
export default defineConfig({
  site: SITE_URL,
  markdown: {
    drafts: true,
    remarkPlugins: [remarkGemoji],
  },
  integrations: [
    mdx({
      drafts: true,
    }),
    sitemap(),
    solidJs(),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
  server: {
    host: true,
    // The dev container publishes port 3000 for Node projects (tdp-template).
    port: 3000
  },
});
