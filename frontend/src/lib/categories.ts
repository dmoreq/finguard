/** Category slug stored in DB; display label shown in UI. */

export function categorySlug(label: string): string {
  return label.trim().toLowerCase();
}

export function categoryDisplay(slug: string): string {
  return slug
    .trim()
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
