import { categories } from "@/features/transactions/types";
import type { AiParseResult, ParseRequest } from "./schemas";

const reportTerms =
  /\b(report|summary|snapshot|overview|balance|status|spent|earned|how much|show me)\b/i;
const incomeTerms =
  /\b(paid|paycheck|salary|earned|income|received|freelance|deposit|bonus|refund|gift)\b/i;
const pendingTerms = /\b(pending|hold|authorization|not posted)\b/i;
const expenseTerms =
  /\b(spent|bought|paid for|purchase|charged|cost|groceries|rent|dinner|lunch|coffee|gas|uber|gym|bill)\b/i;

export function fallbackParse(input: ParseRequest): AiParseResult {
  const message = input.message.trim();
  const amount = extractAmount(message);

  if (!amount && reportTerms.test(message)) {
    return {
      intent: "report",
      message: "Here's your current financial snapshot.",
      transaction: null,
    };
  }

  if (!amount) {
    return {
      intent: "conversation",
      message:
        "Tell me about income or spending in plain language, or ask for a report when you want a snapshot.",
      transaction: null,
    };
  }

  const type = pendingTerms.test(message)
    ? "pending"
    : incomeTerms.test(message) && !expenseTerms.test(message)
      ? "income"
      : "expense";
  const category = inferCategory(message, type);

  return {
    intent: "transaction",
    message: "I found a transaction. Confirm the details below before I save it.",
    transaction: {
      id: `tx-${Date.now()}`,
      type,
      amount,
      category,
      description: cleanDescription(message),
      date: input.today,
      status: "pending_confirmation",
      aiConfidence: 0.62,
    },
  };
}

function extractAmount(message: string) {
  const match = message.match(/(?:\$|usd\s*)?([0-9][0-9,]*(?:\.[0-9]{1,2})?)/i);
  if (!match?.[1]) return null;

  const value = Number.parseFloat(match[1].replaceAll(",", ""));
  return Number.isFinite(value) && value > 0 ? value : null;
}

function inferCategory(message: string, type: "income" | "expense" | "pending") {
  const lower = message.toLowerCase();

  if (type === "income") {
    if (lower.includes("salary") || lower.includes("paycheck")) return "Salary";
    if (lower.includes("freelance") || lower.includes("client")) return "Freelance";
    if (lower.includes("refund")) return "Refund";
    if (lower.includes("gift")) return "Gift";
    return "Other Income";
  }

  if (/grocery|groceries|restaurant|dinner|lunch|coffee|food|meal/.test(lower))
    return "Food & Dining";
  if (/uber|lyft|gas|fuel|bus|train|transport/.test(lower)) return "Transportation";
  if (/rent|mortgage|housing/.test(lower)) return "Housing & Rent";
  if (/electric|water|internet|utility|utilities|bill/.test(lower)) return "Utilities";
  if (/movie|game|concert|entertainment/.test(lower)) return "Entertainment";
  if (/doctor|pharmacy|health|medical/.test(lower)) return "Healthcare";
  if (/shop|amazon|clothes|shopping/.test(lower)) return "Shopping";
  if (/school|course|book|education/.test(lower)) return "Education";
  if (/save|saving|investment/.test(lower)) return "Savings";

  return categories[type][0] ?? "Other";
}

function cleanDescription(message: string) {
  return message.replace(/\s+/g, " ").trim();
}
