import rss from "@astrojs/rss";
import { getCollection } from "astro:content";
import { SITE_TITLE, SITE_DESCRIPTION } from "../consts";

export async function get(context) {
  const posts = await getCollection("entity");
  return rss({
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
    site: context.site,
    items: posts
      .filter((post) => post.data.draft === false)
      .map((post) => ({
        ...post.data,
        link: `/entity/${post.id}/`,
      })),
  });
}
