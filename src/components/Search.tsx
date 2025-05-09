import type { CollectionEntry } from "astro:content";
import Fuse from "fuse.js";
import {
  Show,
  createSignal,
  createMemo,
  createEffect,
  onMount,
} from "solid-js";
import { PostListItem } from "./PostListItem";

interface FuseMatch {
  key: string;
  indices: readonly [number, number][];
}

const options = {
  keys: ["data.title", "data.description", "id"],
  includeMatches: true,
  minMatchCharLength: 2,
  threshold: 0.5,
};

interface Props {
  searchList: CollectionEntry<"entity">[];
}

export default function Search({ searchList }: Props) {
  const fuse = new Fuse(searchList, options);
  const [query, setQuery] = createSignal("");
  const [isLoading, setIsLoading] = createSignal(false);

  const posts = createMemo(() => {
    if (!query().trim()) {
      return [];
    }
    setIsLoading(true);
    const results = fuse.search(query());
    setTimeout(() => setIsLoading(false), 100);
    return results.map(result => ({
      item: result.item,
      matches: (result.matches || []).map(match => ({
        key: match.key || "",
        indices: match.indices || []
      })) as FuseMatch[]
    }));
  });

  // initialize query from URL
  onMount(() => {
    if (typeof window !== "undefined") {
      const searchParams = new URLSearchParams(window.location.search);
      const initialQuery = searchParams.get("q") || "";
      setQuery(initialQuery);
    }
  });

  // Update URL query parameter when the query changes
  createEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    if (query().trim()) {
      searchParams.set("q", query());
    } else {
      searchParams.delete("q");
    }
    const newUrl = `${window.location.pathname}${searchParams.toString() ? "?" + searchParams.toString() : ""}`;
    window.history.replaceState({}, "", newUrl);
  });

  return (
    <div class="space-y-6">
      <label
        for="default-search"
        class="sr-only mb-2 text-sm font-medium text-gray-900 dark:text-white"
      >
        Search
      </label>
      <div class="relative">
        <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
          <svg
            aria-hidden="true"
            class="h-5 w-5 text-gray-500 dark:text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            ></path>
          </svg>
        </div>
        <input
          type="search"
          class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-4 pl-10 text-sm text-gray-900 focus:border-primary-500 focus:outline-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 dark:focus:border-primary-500 dark:focus:ring-primary-500"
          placeholder="Zoek personen en bronnen..."
          required
          id="search"
          onInput={(e) => setQuery(e.target.value)}
          value={query()}
        />
      </div>

      <Show when={query().trim()}>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {posts().length} resultaten gevonden voor "{query()}"
        </p>

        <Show 
          when={!isLoading()} 
          fallback={
            <div class="flex justify-center py-8">
              <div class="h-8 w-8 animate-spin rounded-full border-4 border-primary-500 border-t-transparent"></div>
            </div>
          }
        >
          <Show 
            when={posts().length > 0} 
            fallback={
              <p class="text-center text-gray-600 dark:text-gray-400 py-8">
                Geen resultaten gevonden. Probeer andere zoektermen.
              </p>
            }
          >
            <ul class="grid list-none gap-4 p-0">
              {posts().map((result) => (
                <li class="rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  <PostListItem post={result.item} matches={result.matches} />
                </li>
              ))}
            </ul>
          </Show>
        </Show>
      </Show>
    </div>
  );
}
