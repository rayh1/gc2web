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
  const {
    title,
    branch,
    lifespan,
    birth_place: birthPlace,
    death_place: deathPlace,
    relationship_summary: relationshipSummary,
  } = data;

  const titleMatch = matches.find((match) => match.key === "data.title");
  const placeSummary = [birthPlace, deathPlace].filter(Boolean).join(" → ");

  return (
    <div class="rounded-[1.4rem] border border-archive-line bg-white/80 p-5 shadow-sm transition-colors hover:border-archive-accent/60 hover:bg-white dark:border-archive-dark-line dark:bg-white/5 dark:hover:border-archive-dark-accent/60 dark:hover:bg-white/10">
      <div class="flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.18em] text-archive-muted dark:text-archive-dark-muted">
        {branch && <span>{branch}</span>}
        {lifespan && <span>{lifespan}</span>}
      </div>
      <a
        class="mt-3 block break-words font-display text-xl font-semibold text-archive-ink no-underline transition-colors hover:text-archive-accent dark:text-archive-dark-ink dark:hover:text-archive-dark-accent sm:text-2xl"
        href={`/entity/${id}/`}
      >
        {titleMatch ? highlightText(title, titleMatch.indices) : title}
      </a>
      {relationshipSummary && (
        <p class="mt-3 text-sm leading-6 text-archive-muted dark:text-archive-dark-muted">
          {relationshipSummary}
        </p>
      )}
      {placeSummary && (
        <p class="mt-2 text-sm leading-6 text-archive-muted dark:text-archive-dark-muted">
          {placeSummary}
        </p>
      )}
      <div class="mt-4 text-xs font-medium uppercase tracking-[0.18em] text-archive-muted/80 dark:text-archive-dark-muted/80 break-all">
        ID {id}
      </div>
    </div>
  );
};
