import type { CollectionEntry } from "astro:content";

export const PostListItem = ({ post }: { post: CollectionEntry<"blog"> }) => {
  const { data, slug } = post;
  const { title, description, pubDate, tags } = data;
  return (
    <div class="post flex flex-row h-auto">
      <time class="basis-1/5 italic" datetime={pubDate.toISOString()}>
          {pubDate.toLocaleDateString("nl", {
            year: "numeric",
            month: "short",
            day: "numeric",
          })}
        </time>
        <a 
          class="basis-4/5 text-link no-underline hover:underline"
          href={`/blog/${slug}/`}
        >
          {title}
        </a>
    </div>
  );
};
