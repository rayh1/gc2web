import type { CollectionEntry } from "astro:content";

export const PostListItem = ({ post }: { post: CollectionEntry<"entity"> }) => {
  const { data, id } = post;
  const { title, description, pubDate, tags } = data;
  return (
    <div class="post flex flex-row h-auto">
        <a 
          class="basis-4/5 text-link no-underline hover:underline"
          href={`/entity/${id}/`}
        >
          {title}
        </a>
    </div>
  );
};
