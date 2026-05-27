# Finguard Next.js Implementation Plan

Date: 2026-05-27

## Decision

Build Finguard as a full-stack Next.js App Router application under `frontend/`.

This means Next.js owns both:

- The frontend: authenticated app pages, chat UI, dashboard UI, transaction forms, responsive layout.
- The backend boundary: route handlers/server functions for AI parsing, transaction mutations, export/delete flows, and any future integrations.

Use Supabase for Auth and Postgres persistence. Next.js should not replace the database layer; it should coordinate authenticated server-side work and render the product.

## Why Next.js Fits This Version

The earlier Vite recommendation optimized for the shortest route from prototype to web MVP. Your preference for option 3 changes the optimization target: we now value a unified full-stack web product over the smallest migration.

Next.js is appropriate because Finguard will likely need:

- Server-side AI calls without exposing provider keys.
- Authenticated pages with protected server-side data access.
- A real dashboard/reporting surface.
- Public pages later: pricing, privacy, terms, marketing, changelog, help docs.
- Route handlers for future mobile/API clients.
- Strong deployment fit on Vercel or any Node-compatible platform.

The key engineering discipline is to keep the interactive chat/dashboard as client components, while keeping AI, auth checks, persistence, and sensitive logic on the server.

## Official References

- Next.js App Router is file-system based and uses Server Components, Suspense, and Server Functions: [Next.js App Router docs](https://nextjs.org/docs/app).
- Next.js Server Components are default; Client Components are needed for state, event handlers, effects, and browser APIs: [Next.js Server and Client Components docs](https://nextjs.org/docs/app/getting-started/server-and-client-components).
- Next.js Server Functions/Server Actions run on the server and must verify auth/authorization: [Next.js Mutating Data docs](https://nextjs.org/docs/app/getting-started/mutating-data).
- Supabase supports Next.js App Router auth with cookie-based SSR setup: [Supabase Next.js Auth docs](https://supabase.com/docs/guides/auth/quickstarts/nextjs).
- Supabase SSR stores auth session in cookies so server and client can both access session state: [Supabase SSR docs](https://supabase.com/docs/guides/auth/server-side).
- OpenAI Structured Outputs reliably match model output to a provided schema, unlike plain JSON mode: [OpenAI Structured Outputs docs](https://platform.openai.com/docs/guides/structured-outputs).

## Recommended Stack

| Layer | Choice | Reason |
| --- | --- | --- |
| Web framework | Next.js App Router + TypeScript | Full-stack routing, server/client component model, route handlers, deployment maturity. |
| UI styling | Tailwind CSS + CSS variables | Fast migration from inline style values; easy responsive states; compatible with shadcn/ui later. |
| UI primitives | Radix UI or shadcn/ui selectively | Use for dialogs, menus, tabs, tooltips, forms; avoid hand-rolling accessibility. |
| Icons | lucide-react | Consistent icon buttons for dashboard/chat actions. |
| Auth | Supabase Auth | Simple email/OAuth flows, SSR guidance, Postgres identity integration. |
| Database | Supabase Postgres | Relational fit for transactions, categories, accounts, audit history, and reports. |
| Access control | Supabase Row Level Security | Enforce user-owned rows at DB level. |
| Validation | Zod | Shared schemas for AI outputs, forms, route handlers, and server actions. |
| AI | Server route using structured outputs | Keeps keys server-side and replaces regex JSON parsing. |
| Client data | TanStack Query or SWR | Good for chat/dashboard cache, optimistic updates, retries. |
| Server mutations | Server Actions for app-only mutations; Route Handlers for public/API-like calls | Use the right interface per boundary. |
| Tests | Vitest + Testing Library + Playwright | Unit-test finance calculations, integration-test main workflow. |
| Deployment | Vercel first | Best native support for Next.js, route handlers, env management, previews. |

## High-Level Architecture

```text
Browser
  Next.js Client Components
    Chat workspace
    Input bar
    Transaction confirmation card
    Dashboard panel
    Settings/forms

Next.js Server
  Server Components
    Protected page shells
    Initial transaction fetch
    Account/settings fetch

  Server Actions
    createTransaction
    updateTransaction
    deleteTransaction
    clearChatHistory
    updatePreferences

  Route Handlers
    POST /api/ai/parse
    GET  /api/export/transactions.csv
    POST /api/account/delete
    future: /api/webhooks/*

Supabase
  Auth
  Postgres
  RLS policies
  optional Storage for receipts later

LLM Provider
  Structured transaction/report parser
```

## Route Map

Use route groups to separate public and authenticated surfaces.

```text
frontend/src/app/
  (public)/
    page.tsx                    # Optional landing page later
    privacy/page.tsx
    terms/page.tsx
  (auth)/
    sign-in/page.tsx
    sign-up/page.tsx
    callback/route.ts           # Supabase auth callback
  (app)/
    layout.tsx                  # Protected app shell
    page.tsx                    # Redirect to /chat or render main workspace
    chat/page.tsx               # Main Finguard product screen
    transactions/page.tsx       # Table/list view after MVP
    reports/page.tsx            # Larger reporting view after MVP
    settings/page.tsx
  api/
    ai/parse/route.ts
    export/transactions.csv/route.ts
    account/delete/route.ts
```

MVP route priority:

1. `(auth)/sign-in`
2. `(auth)/sign-up`
3. `(app)/chat`
4. `api/ai/parse`
5. Transaction server actions

Defer public landing, reports route, transactions route, and account deletion UI until the core loop is stable.

## Component Boundary

Next.js defaults to Server Components. Only mark interactive files with `"use client"`.

Server Components:

- `frontend/src/app/(app)/layout.tsx`
- `frontend/src/app/(app)/chat/page.tsx`
- `frontend/src/features/chat/ChatPageData.tsx`
- server-only data loaders under `frontend/src/server`

Client Components:

- `frontend/src/features/chat/ChatWorkspace.tsx`
- `frontend/src/features/chat/InputBar.tsx`
- `frontend/src/features/chat/MessageBubble.tsx`
- `frontend/src/features/transactions/TransactionCard.tsx`
- `frontend/src/features/reports/DashboardPanel.tsx`
- `frontend/src/features/reports/ReportCard.tsx`

Rule of thumb:

- If it uses `useState`, `useEffect`, `onClick`, `onChange`, `textarea`, optimistic UI, `localStorage`, or live chat state, it is a Client Component.
- If it reads the authenticated user, loads initial DB data, redirects unauthenticated users, or calls secrets, it stays server-side.

## Proposed File Structure

```text
frontend/
  src/
    app/                         # Next.js app directory
    components/
      ui/
        button.tsx
        input.tsx
        textarea.tsx
        tabs.tsx
        dialog.tsx
        tooltip.tsx
      layout/
        AppHeader.tsx
        AppShell.tsx
    features/
      chat/
        ChatWorkspace.tsx
        InputBar.tsx
        MessageBubble.tsx
        TypingIndicator.tsx
        ai-client.ts
        types.ts
      transactions/
        TransactionCard.tsx
        TransactionList.tsx
        actions.ts
        schemas.ts
        types.ts
      reports/
        DashboardPanel.tsx
        ReportCard.tsx
        finance-calculations.ts
        charts/
          DonutChart.tsx
          BarRow.tsx
      auth/
        SignInForm.tsx
        SignUpForm.tsx
    lib/
      env.ts
      format.ts
      dates.ts
      errors.ts
      supabase/
        client.ts
        server.ts
        middleware.ts
    server/
      ai/
        parse-transaction.ts
        prompt.ts
        schemas.ts
      db/
        transactions.ts
        messages.ts
        preferences.ts
    styles/
      globals.css
```

## Data Model

Start small, but model the product as real user-owned data from day one.

### Tables

```sql
create type transaction_type as enum ('income', 'expense', 'pending');

create table profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  currency text not null default 'USD',
  timezone text not null default 'UTC',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table categories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  type transaction_type not null,
  name text not null,
  is_default boolean not null default false,
  created_at timestamptz not null default now(),
  unique (user_id, type, name)
);

create table transactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  type transaction_type not null,
  amount numeric(12, 2) not null check (amount >= 0),
  currency text not null default 'USD',
  category text not null,
  description text,
  transaction_date date not null,
  status text not null default 'confirmed' check (status in ('pending_confirmation', 'confirmed', 'discarded')),
  source text not null default 'manual_chat' check (source in ('manual_chat', 'manual_form', 'import', 'integration')),
  ai_confidence numeric(4, 3),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table chat_messages (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  message_type text not null default 'text' check (message_type in ('text', 'transaction', 'report', 'error')),
  transaction_id uuid references transactions(id) on delete set null,
  metadata jsonb not null default '{}',
  created_at timestamptz not null default now()
);
```

### RLS Policies

Enable RLS for every user data table.

```sql
alter table profiles enable row level security;
alter table categories enable row level security;
alter table transactions enable row level security;
alter table chat_messages enable row level security;

create policy "profiles are user-owned"
on profiles for all
using (auth.uid() = id)
with check (auth.uid() = id);

create policy "categories are user-owned"
on categories for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create policy "transactions are user-owned"
on transactions for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create policy "chat messages are user-owned"
on chat_messages for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);
```

Default categories can be represented either as seeded per-user rows at signup or as app-level constants. For MVP, constants are simpler. Move to persisted custom categories when users can edit category lists.

## AI Parsing Design

Replace this prototype behavior:

```js
const raw = await window.claude.complete(buildPrompt(text, today, transactions));
const m = raw.match(/\{[\s\S]*\}/);
parsed = JSON.parse(m[0]);
```

With:

```text
Client Component
  POST /api/ai/parse { message }

Route Handler
  verify session
  fetch small financial context
  call LLM with structured schema
  validate result with Zod
  return typed JSON

Client Component
  render transaction confirmation card or report
```

### AI Response Schema

```ts
const aiParseResultSchema = z.object({
  intent: z.enum(['transaction', 'report', 'conversation']),
  message: z.string().min(1),
  transaction: z
    .object({
      type: z.enum(['income', 'expense', 'pending']),
      amount: z.number().positive(),
      category: z.string().min(1),
      description: z.string().nullable(),
      date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
      confidence: z.number().min(0).max(1),
    })
    .nullable(),
});
```

### Route Handler Shape

Use a route handler for AI parsing rather than a Server Action because it is a clear API boundary and can later be reused by a mobile app.

```ts
// frontend/src/app/api/ai/parse/route.ts
export async function POST(request: Request) {
  const supabase = await createServerSupabaseClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const body = await request.json();
  const input = parseRequestSchema.parse(body);

  const context = await getFinancialContext(user.id);
  const result = await parseTransactionWithAI({
    userMessage: input.message,
    today: input.today,
    context,
  });

  return Response.json(result);
}
```

### Prompt Rules

The server prompt should:

- Ask only for schema output.
- Include the user's currency and timezone.
- Include limited aggregate context, not full transaction history unless needed.
- Explain category rules.
- Require `confidence`.
- Require `intent = report` for summary/report/balance/status requests.
- Never save a transaction automatically. The frontend confirmation flow remains mandatory.

## Transaction Mutation Design

Use Server Actions for app-owned mutations from the Next.js UI:

- `confirmParsedTransaction`
- `createManualTransaction`
- `updateTransaction`
- `deleteTransaction`
- `discardParsedTransaction`

Why Server Actions here:

- These are internal app mutations.
- They need auth checks and cache revalidation.
- They pair cleanly with forms and optimistic UI.

Keep route handlers for:

- AI parsing.
- CSV export.
- Webhooks.
- Future mobile app API.

## Main User Flow

1. User signs in.
2. Server-rendered chat page loads the user profile and recent transactions.
3. `ChatWorkspace` hydrates with initial data.
4. User enters: `Spent $45 on groceries`.
5. Client posts to `/api/ai/parse`.
6. Server verifies session and calls AI with structured schema.
7. Client renders assistant message plus `TransactionCard`.
8. User edits if needed and clicks Save.
9. Server Action inserts transaction and assistant confirmation message.
10. Dashboard revalidates and updates totals.

## Migration From Prototype

### `prototype/app.jsx`

Split into:

- `ChatWorkspace.tsx`: chat state, input handling, rendering messages.
- `InputBar.tsx`: textarea and send button.
- `MessageBubble.tsx`: user/assistant bubble rendering.
- `server/ai/prompt.ts`: current `buildPrompt`, rewritten for structured outputs.
- `features/reports/finance-calculations.ts`: current `computeReportData`.

Remove:

- `window.claude.complete`
- `localStorage` as source of truth
- `dangerouslySetInnerHTML` markdown rendering unless replaced with a safe markdown renderer
- browser-global component references

### `prototype/transaction-card.jsx`

Convert to:

- `features/transactions/TransactionCard.tsx`
- Typed props
- Controlled draft state
- Accessible buttons/inputs
- Server Action call on save
- Better status model: `pending_confirmation`, `confirmed`, `discarded`

### `prototype/dashboard.jsx`

Convert to:

- `features/reports/DashboardPanel.tsx`
- `features/reports/charts/DonutChart.tsx`
- `features/reports/charts/BarRow.tsx`
- `features/reports/finance-calculations.ts`

Make calculations pure and unit-tested.

## Styling Plan

The prototype relies on extensive inline styles. In Next.js, move to:

- `globals.css` for theme tokens:
  - colors
  - typography
  - spacing
  - radius
  - shadows
- Tailwind utility classes for layout and component state.
- Component-level helpers for repeated financial status colors.

Example token direction:

```css
:root {
  --fg-bg: oklch(0.97 0.007 250);
  --fg-surface: #fff;
  --fg-border: oklch(0.93 0.006 250);
  --fg-primary: oklch(0.52 0.18 165);
  --fg-income: oklch(0.50 0.18 145);
  --fg-expense: oklch(0.56 0.17 22);
  --fg-pending: oklch(0.68 0.15 72);
}
```

Keep the current visual identity for MVP. Do not redesign while migrating frameworks.

## Authentication Plan

Use Supabase Auth with SSR cookies.

Required files:

```text
frontend/src/lib/supabase/client.ts      # Browser client
frontend/src/lib/supabase/server.ts      # Server Component, Server Action, Route Handler client
middleware.ts                   # Refresh session and protect app routes
frontend/src/app/(auth)/callback/route.ts    # OAuth/email callback
```

Route protection:

- Redirect unauthenticated users from `(app)` routes to `/sign-in`.
- Redirect authenticated users away from `/sign-in` and `/sign-up` to `/chat`.
- Always verify auth again in Server Actions and Route Handlers. Middleware is not enough.

## Environment Variables

```bash
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=
SUPABASE_SERVICE_ROLE_KEY=

OPENAI_API_KEY=
AI_MODEL=

APP_URL=http://localhost:3000
```

Rules:

- Only `NEXT_PUBLIC_*` variables are available to browser code.
- Never expose `SUPABASE_SERVICE_ROLE_KEY` or `OPENAI_API_KEY` to Client Components.
- Prefer normal authenticated Supabase clients plus RLS. Use service role only for admin-only operations like complete account deletion, and isolate that code.

## Security Requirements

Minimum bar for a finance app:

- Enforce RLS on all user-owned tables.
- Validate every route handler body with Zod.
- Validate every Server Action input with Zod.
- Verify auth inside every Server Action and Route Handler.
- Rate-limit `/api/ai/parse` per user and IP.
- Do not store provider raw responses unless needed for debugging, and redact sensitive content.
- Keep the confirmation-card step. AI should propose transactions, not silently create them.
- Add account data export and deletion before public launch.
- Add a privacy policy before collecting real user data.

## Caching and Freshness

For authenticated financial data, favor correctness over aggressive caching.

Recommendations:

- Fetch initial transaction data in Server Components with the authenticated server Supabase client.
- Use Server Actions to mutate transactions and call `revalidatePath('/chat')` or update client cache optimistically.
- Do not cache AI parse responses globally.
- Do not statically render authenticated app pages.
- Public pages can be static.

## Testing Plan

Unit tests:

- `computeReportData`
- category aggregation
- monthly filtering
- currency/date formatting
- Zod schemas for AI parse results

Component tests:

- `TransactionCard` edit/save/discard states
- `InputBar` enter-to-send behavior
- `DashboardPanel` empty/data states

Playwright tests:

- sign in
- submit transaction text
- parse result appears as confirmation card
- save transaction
- dashboard totals update
- discard transaction does not create DB row

Security tests:

- user A cannot read user B transactions.
- unauthenticated route handler request returns 401.
- invalid AI parse input returns 400.

## Implementation Phases

### Phase 0: Scaffold

- Create Next.js App Router project with TypeScript and Tailwind.
- Install Supabase packages, Zod, lucide-react, test tooling.
- Add base layout, fonts, theme tokens, and lint/typecheck scripts.

### Phase 1: Auth and Protected Shell

- Configure Supabase SSR clients.
- Add sign-in/sign-up/callback routes.
- Add middleware route protection.
- Add `(app)/chat` protected page.
- Verify authenticated server-side user load.

Exit criteria:

- User can sign up, sign in, sign out.
- `/chat` is inaccessible while signed out.

### Phase 2: Database and Server Data

- Add database migrations for profiles, transactions, chat messages.
- Enable RLS and owner policies.
- Seed default categories in code.
- Load recent transactions in `chat/page.tsx`.

Exit criteria:

- Authenticated user sees only their own transaction data.
- Basic transaction insert/read works server-side.

### Phase 3: Port UI

- Port chat, input bar, message bubbles, transaction card, dashboard, report card.
- Replace globals with imports.
- Replace inline duplicated styling with Tailwind/classes.
- Keep the existing design and behavior.

Exit criteria:

- UI matches prototype closely.
- Static local sample data renders correctly.

### Phase 4: AI Parse Endpoint

- Add `/api/ai/parse`.
- Add structured output schema and Zod validation.
- Connect `ChatWorkspace` to the route handler.
- Render transaction/report/conversation responses.

Exit criteria:

- User text produces typed parse results.
- No API key exists in browser bundle.
- Invalid parser output fails safely.

### Phase 5: Confirm and Persist

- Add `confirmParsedTransaction` Server Action.
- Add discard behavior.
- Persist chat messages and confirmed transactions.
- Recompute dashboard from server data.

Exit criteria:

- Full prototype workflow works with authenticated database data.

### Phase 6: MVP Hardening

- Add error, retry, empty, loading, and offline states.
- Add transaction edit/delete after save.
- Add CSV export.
- Add account data deletion route.
- Add Playwright tests.
- Add rate limiting for AI endpoint.

Exit criteria:

- App is safe enough for private beta with real users.

## Suggested MVP Scope

Include:

- Email auth.
- Chat-based manual transaction entry.
- AI parse with confirmation card.
- Edit before saving.
- Income/expense/pending transaction types.
- Dashboard sidebar with monthly overview.
- Transaction history.
- CSV export.
- Account data delete.

Defer:

- Bank account integrations.
- Receipt OCR.
- Recurring transactions.
- Budgets.
- Multi-currency conversion.
- Shared households.
- Native mobile app.
- Advanced tax/accounting reports.

## Open Decisions

1. AI provider: OpenAI, Anthropic, or model-agnostic adapter?
2. Auth methods: email/password only, magic link, Google OAuth, or all three?
3. Deployment: Vercel + Supabase, or a custom Node hosting environment?
4. Styling: pure Tailwind or Tailwind plus shadcn/ui?
5. Data retention: should chat history be permanent, user-configurable, or ephemeral after transaction extraction?
6. Currency scope: USD-only for MVP, or user-selected currency with no exchange conversion?

## Recommendation

Proceed with Next.js App Router, Supabase Auth/Postgres/RLS, and a route-handler AI boundary.

Use Server Components for protected page shells and initial data loading. Use Client Components for the chat workspace and dashboard interactivity. Use Server Actions for internal transaction mutations. Use Route Handlers for AI parsing, exports, webhooks, and future external clients.

This gives you the full-stack structure you prefer without losing the prototype's strongest asset: a fast, conversational transaction-entry workflow.
