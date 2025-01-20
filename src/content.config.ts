import { defineCollection, z } from "astro:content";
import { glob } from 'astro/loaders';

const blogCollection = defineCollection({
  loader: glob({ pattern: '**/[^_]*.{md,mdx}', base: "./src/content/entity" }),
  schema: z.object({
    tags: z.array(z.string()).default([]), // the same as the filename without the extension
    title: z.string(),
    draft: z.boolean().default(false),
    description: z.string(),
    // Transform string to Date object
    pubDate: z
      .string()
      .or(z.date())
      .transform((val) => new Date(val)),
    updatedDate: z
      .string()
      .optional()
      .transform((str) => (str ? new Date(str) : undefined)),
    heroImage: z.string().optional(),
  }),
});

const tagCollection = defineCollection({
  loader: glob({ pattern: '**/[^_]*.{md,mdx}', base: "./src/content/tag" }),
  schema: z.object({
    title: z.string(),
  }),
});

export const collections = {
  'entity': blogCollection,
  'tag': tagCollection 
};
