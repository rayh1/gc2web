import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";
import solidJs from "@astrojs/solid-js";
import tailwind from "@astrojs/tailwind";
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
    tailwind(),
  ],
  server: {
    host: true
  },
});
