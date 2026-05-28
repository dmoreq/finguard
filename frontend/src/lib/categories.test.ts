import { describe, expect, it } from "vitest";
import { categoryDisplay, categorySlug } from "./categories";

describe("categories", () => {
  it("slugifies labels for Rasa/DB", () => {
    expect(categorySlug("Food & Dining")).toBe("food & dining");
  });

  it("displays slugs in title case for English locale", () => {
    expect(categoryDisplay("food & dining", "en")).toBe("Food & Dining");
  });

  it("displays Vietnamese labels when locale is vi", () => {
    expect(categoryDisplay("dining", "vi")).toBe("Ăn uống");
  });
});
