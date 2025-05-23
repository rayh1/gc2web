import { defineCollection, z } from "astro:content";
import { glob } from 'astro/loaders';

const blogCollection = defineCollection({
  loader: glob({ pattern: '**/[^_]*.{md,mdx}', base: "./src/content/entity" }),
  schema: z.object({
    title: z.string()
  }),
});

export const collections = {
  'entity': blogCollection
};
