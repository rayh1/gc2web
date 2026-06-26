import { render, screen } from "@solidjs/testing-library";
import { describe, expect, it } from "vitest";

import { PostListItem } from "../PostListItem";

const richPost = {
  id: "i00005",
  data: {
    title: "Petrus Johannes Hoofman (1890-1972)",
    branch: "Hoofman",
    lifespan: "(1890-1972)",
    birth_place: "Muiden",
    death_place: "Amsterdam",
    relationship_summary: "Partner van Wilhelmina Johanna Voorbraak",
  },
} as any;

describe("PostListItem", () => {
  it("renders contextual metadata when available", () => {
    render(() => <PostListItem post={richPost} />);

    expect(screen.getByText("Hoofman")).toBeTruthy();
    expect(screen.getByText("Partner van Wilhelmina Johanna Voorbraak")).toBeTruthy();
    expect(screen.getByText("Muiden → Amsterdam")).toBeTruthy();
  });

  it("falls back to title and id when metadata is missing", () => {
    render(() => <PostListItem post={{ id: "i00123", data: { title: "Naam zonder context" } } as any} />);

    expect(screen.getByText("Naam zonder context")).toBeTruthy();
    expect(screen.getByText(/ID i00123/)).toBeTruthy();
  });
});
