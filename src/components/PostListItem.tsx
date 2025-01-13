import type { CollectionEntry } from "astro:content";

export const PostListItem = ({ post }: { post: CollectionEntry<"entity"> }) => {
  const { data, slug } = post;
  const { title, description, pubDate, tags } = data;
  return (
    <div class="post flex flex-row h-auto">
        <a 
          class="basis-4/5 text-link no-underline hover:underline"
          href={`/entity/${slug}/`}
        >
          {title}
        </a>
    </div>
  );
};
