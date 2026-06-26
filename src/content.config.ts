import { defineCollection, z } from "astro:content";
import { glob } from 'astro/loaders';

const blogCollection = defineCollection({
  loader: glob({ pattern: '**/[^_]*.{md,mdx}', base: "./src/content/entity" }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    pubDate: z.string().optional(),
    lifespan: z.string().optional(),
    birth_place: z.string().optional(),
    death_place: z.string().optional(),
    relationship_summary: z.string().optional(),
    branch: z.string().optional(),
    section_order: z.array(z.string()).optional(),
  }),
});

export const collections = {
  'entity': blogCollection
};
