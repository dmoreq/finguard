import { describe, expect, it } from "vitest";
import { categoryDisplay, categorySlug } from "./categories";

describe("categories", () => {
  it("slugifies labels for Rasa/DB", () => {
    expect(categorySlug("Food & Dining")).toBe("food & dining");
  });

  it("displays slugs in title case", () => {
    expect(categoryDisplay("food & dining")).toBe("Food & Dining");
  });
});
