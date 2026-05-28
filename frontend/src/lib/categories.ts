/** Category slug stored in DB; display label shown in UI. */

const VI_LABELS: Record<string, string> = {
  dining: "Ăn uống",
  groceries: "Chợ / siêu thị",
  transport: "Đi lại",
  salary: "Lương",
  rent: "Tiền nhà",
  utilities: "Tiện ích",
  freelance: "Freelance",
  coffee: "Cà phê",
  entertainment: "Giải trí",
  shopping: "Mua sắm",
  health: "Sức khỏe",
  bills: "Hóa đơn",
  travel: "Du lịch",
};

export function categorySlug(label: string): string {
  return label.trim().toLowerCase();
}

export function categoryDisplay(slug: string, locale = "vi"): string {
  const base = slug.trim().toLowerCase();
  if (locale.startsWith("vi") && VI_LABELS[base]) {
    return VI_LABELS[base];
  }
  return base
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export const CATEGORY_OPTIONS = [
  { slug: "dining", vi: "Ăn uống", en: "Dining" },
  { slug: "groceries", vi: "Chợ / siêu thị", en: "Groceries" },
  { slug: "transport", vi: "Đi lại", en: "Transport" },
  { slug: "salary", vi: "Lương", en: "Salary" },
  { slug: "rent", vi: "Tiền nhà", en: "Rent" },
  { slug: "utilities", vi: "Tiện ích", en: "Utilities" },
  { slug: "freelance", vi: "Freelance", en: "Freelance" },
  { slug: "shopping", vi: "Mua sắm", en: "Shopping" },
  { slug: "entertainment", vi: "Giải trí", en: "Entertainment" },
];

export function welcomeMessage(locale: string): string {
  if (locale.startsWith("vi")) {
    return 'Xin chào! Tôi là **Finguard**, trợ lý tài chính của bạn.\n\nBạn có thể nói bằng tiếng Việt:\n- *"Nhận lương 15 triệu"*\n- *"Chi tiêu 80k cà phê"*\n- *"Tháng nay chi bao nhiêu?"*\n\nTôi sẽ ghi giao dịch để bạn xác nhận trước khi lưu.';
  }
  return 'Hi! I\'m **Finguard**, your AI financial assistant.\n\nTell me about your finances in plain language:\n- *"I got paid $3,200 today"*\n- *"Spent $45 on groceries"*\n- *"Show me my spending report"*\n\nI\'ll record transactions for you to confirm, and summarize your spending when you ask.';
}

export function inputPlaceholder(locale: string): string {
  if (locale.startsWith("vi")) {
    return 'Ví dụ: "Chi tiêu 50k cà phê" hoặc "Số dư tháng nay"...';
  }
  return 'e.g. "I got paid $3,200" or "Spent $45 on groceries"...';
}
