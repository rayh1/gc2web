import type { CollectionEntry } from "astro:content";
import { For } from "solid-js";

interface FuseMatch {
  key: string;
  indices: readonly [number, number][];
}

interface Props {
  post: CollectionEntry<"entity">;
  matches?: readonly FuseMatch[];
}

function highlightText(text: string, indices: readonly [number, number][]) {
  if (!indices || indices.length === 0) return text;

  const segments: { text: string; highlight: boolean }[] = [];
  let lastIndex = 0;

  indices.forEach(([start, end]) => {
    if (start > lastIndex) {
      segments.push({ text: text.substring(lastIndex, start), highlight: false });
    }
    segments.push({ text: text.substring(start, end + 1), highlight: true });
    lastIndex = end + 1;
  });

  if (lastIndex < text.length) {
    segments.push({ text: text.substring(lastIndex), highlight: false });
  }

  return (
    <For each={segments}>
      {(segment) => 
        segment.highlight ? (
          <span class="bg-yellow-100 dark:bg-yellow-900 rounded px-0.5">{segment.text}</span>
        ) : (
          segment.text
        )
      }
    </For>
  );
}

export const PostListItem = ({ post, matches = [] }: Props) => {
  const { data, id } = post;
  const { title } = data;

  const titleMatch = matches.find((match) => match.key === "data.title");

  return (
    <div class="flex flex-col gap-1">
      <a 
        class="text-lg font-medium text-primary-500 no-underline hover:underline dark:text-primary-400"
        href={`/entity/${id}/`}
      >
        {titleMatch ? highlightText(title, titleMatch.indices) : title}
      </a>
      <div class="text-xs text-gray-500 dark:text-gray-500">
        ID: {id}
      </div>
    </div>
  );
};
