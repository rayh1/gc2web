import { fireEvent, render, screen, waitFor } from "@solidjs/testing-library";
import { beforeEach, describe, expect, it } from "vitest";

import Search from "../Search";

const searchList = [
  {
    id: "i00005",
    data: {
      title: "Petrus Johannes Hoofman (1890-1972)",
      description: "Individual",
      relationship_summary: "Partner van Wilhelmina Johanna Voorbraak",
      branch: "Hoofman",
      birth_place: "Muiden",
      death_place: "Amsterdam",
      lifespan: "(1890-1972)",
    },
  },
] as any;

describe("Search", () => {
  beforeEach(() => {
    window.history.replaceState({}, "", "/search");
  });

  it("finds results through contextual metadata", async () => {
    render(() => <Search searchList={searchList} />);

    fireEvent.input(screen.getByRole("searchbox"), {
      target: { value: "Wilhelmina" },
    });

    await waitFor(() => {
      expect(screen.getByText(/1 resultaten gevonden/)).toBeTruthy();
      expect(screen.getByText("Partner van Wilhelmina Johanna Voorbraak")).toBeTruthy();
    });
  });

  it("shows the empty state when no result matches", async () => {
    render(() => <Search searchList={searchList} />);

    fireEvent.input(screen.getByRole("searchbox"), {
      target: { value: "onbestaand" },
    });

    await waitFor(() => {
      expect(screen.getByText(/Geen resultaten gevonden/)).toBeTruthy();
    });
  });
});
