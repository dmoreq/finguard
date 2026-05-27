# Finguard Prototype to Product Options

Date: 2026-05-27

## Executive Summary

The prototype is a strong interaction demo for an AI financial assistant: chat input, transaction extraction, editable confirmation cards, local transaction history, and a reporting sidebar. It is not production-ready yet because it runs as a static browser page with CDN React, browser Babel, global components, `localStorage`, and a direct `window.claude.complete(...)` dependency.

Best recommendation: build a web-first MVP as a Vite React + TypeScript single-page app, backed by Supabase and a server-side AI endpoint. This keeps the current prototype closest to its existing shape, gives the fastest path to a usable product, and avoids prematurely paying the complexity cost of native mobile or full-stack SSR. Add PWA support after the first working web version if mobile installability matters.

## Prototype Assessment

Current files:

- `prototype/index.html`: loads React, ReactDOM, and Babel from CDNs, then loads JSX files directly in the browser.
- `prototype/app.jsx`: owns chat state, transaction state, prompt construction, local persistence, and the main layout.
- `prototype/transaction-card.jsx`: transaction confirmation/editing UI and inline report card.
- `prototype/dashboard.jsx`: reporting sidebar, category charts, summary stats, and transaction lists.

What works well:

- Clear core workflow: natural-language entry -> AI parse -> confirm card -> saved transaction -> dashboard.
- Product shape is obvious and compact; the prototype already expresses the MVP experience.
- UI is mostly componentized, even though components are currently global.
- The reporting logic is simple enough to extract into pure utilities and test.

Production blockers:

- No package manager, bundler, type checking, linting, test runner, or deploy pipeline.
- Browser Babel and CDN React are fine for a prototype but not for shipped code.
- `window.claude.complete(...)` implies an LLM call from the browser. A production app should route AI calls through a server endpoint so API keys, rate limits, logging, validation, and abuse controls stay server-side.
- AI JSON parsing is fragile. The code asks for JSON and then regex-extracts an object from raw text.
- User financial data is stored only in `localStorage`, so it is device-local, unauthenticated, unsynced, and easy to lose.
- There is no user model, access control, data export, deletion flow, privacy policy surface, or audit trail.
- Inline styles and hand-drawn SVGs make the UI harder to scale, theme, and test.

## Researched Signals

- React's current guidance points teams toward frameworks for real apps, including Next.js for full-stack React and Expo for native apps; when starting from scratch, React also notes Vite as a build-tool path if you are assembling your own app architecture. Source: [React docs](https://react.dev/learn/creating-a-react-app).
- Vite supports a `react-ts` template, which is the lightest direct migration path from the current JSX prototype into a maintainable React app. Source: [Vite docs](https://vite.dev/guide/).
- Next.js is a React framework for full-stack web applications and includes server/client rendering architecture, routing, and build configuration. Source: [Next.js docs](https://nextjs.org/docs).
- Expo is the React path for universal Android, iOS, and web apps with native UI; Expo Router supports file-based routing across native and web. Sources: [React docs](https://react.dev/learn/creating-a-react-app), [Expo Router docs](https://docs.expo.dev/develop/file-based-routing).
- OpenAI Structured Outputs are preferable to prompt-only JSON mode where supported because they enforce schema adherence, not just valid JSON. Source: [OpenAI Structured Outputs docs](https://developers.openai.com/api/docs/guides/structured-outputs).
- Supabase Row Level Security is a strong fit for user-owned financial records because policies can enforce per-user data access in Postgres. Source: [Supabase RLS docs](https://supabase.com/docs/guides/database/postgres/row-level-security).
- Firebase/Firestore is also viable; Firestore Security Rules can enforce auth-based document access. Source: [Firebase Security Rules docs](https://firebase.google.com/docs/firestore/security/rules-conditions).

## Options

| Option | What It Means | Pros | Cons | Best For |
| --- | --- | --- | --- | --- |
| 1. Static prototype hardening | Keep a static React page, remove browser Babel, bundle assets, keep `localStorage`. | Fastest demo path; minimal rewrite. | Not suitable for real financial data; no auth, sync, backend validation, or secure AI key handling. | Investor/demo prototype only. |
| 2. Vite React SPA + backend services | Convert JSX to a Vite React TypeScript app, add a serverless AI API, auth, database, and PWA later. | Closest to current code; fast MVP; simple mental model; easy deploy; works well for chat-heavy app UI. | You must choose and wire backend services; no built-in SSR. | Recommended web MVP. |
| 3. Next.js full-stack app | Rebuild as Next.js App Router with API routes/server actions, auth, database, and React client components for chat. | Strong full-stack conventions; server-side AI calls fit naturally; good for dashboards, auth pages, billing, content, SEO. | More architecture than this prototype currently needs; server/client boundaries add complexity for a mostly client-side chat workspace. | Product with marketing site, SEO, billing, server-rendered pages, or a larger team. |
| 4. Expo universal app | Rebuild UI in React Native/Expo for iOS, Android, and web. | Best long-term mobile app path; native notifications, biometrics, camera/receipt capture, app store distribution. | Largest UI rewrite because DOM elements/styles do not port directly; web dashboard layout must be adapted to native screens. | Mobile-first personal finance app. |
| 5. Two-track web + native later | Ship web MVP first, then build an Expo app once workflows and data model stabilize. | Reduces early risk; validates AI parsing and finance UX before native rewrite. | Some UI work will be duplicated later unless a shared design system and domain package are planned early. | Sensible path if native is important but not required for launch. |

## Recommended Path

Choose option 2: Vite React SPA + TypeScript + Supabase + server-side AI endpoint.

Reasoning:

- The prototype is already a client-heavy app, not a content site. Vite preserves that shape with the least rewrite.
- A secure AI endpoint is mandatory either way. Vite can pair cleanly with Supabase Edge Functions, Vercel Functions, Netlify Functions, Cloudflare Workers, or a small Node API.
- Supabase gives a relational model that fits transactions, categories, user profiles, audit metadata, and future analytics better than a document-only model.
- Row Level Security is important for a financial app; user-owned rows should be enforced at the database boundary, not only in frontend code.
- TypeScript and schema validation can turn the AI parse result into a real contract instead of regex-extracted JSON.

Recommended stack:

- Frontend: Vite, React, TypeScript.
- Styling: CSS Modules or Tailwind. Tailwind is faster for iteration; CSS Modules are quieter and closer to the existing hand-tuned UI.
- State: Zustand for client UI state, TanStack Query for server state.
- Forms/schema: Zod for transaction schemas and AI response validation.
- Database/auth: Supabase Auth + Postgres + RLS.
- AI route: serverless function using structured outputs or tool/function calling. Never call the model provider directly from the browser.
- Charts: keep current SVG charts for MVP, or move to Recharts/Visx once reporting expands.
- Testing: Vitest for utilities/components, Playwright for the chat-to-confirm-to-save workflow.

## Target Architecture

```text
Browser React app
  -> Auth session
  -> /api/parse-transaction
      -> LLM provider with schema-constrained output
      -> validates with Zod
      -> returns typed parse result
  -> Supabase client
      -> transactions table
      -> categories table
      -> user_preferences table
      -> RLS enforces user_id ownership
```

Key implementation decisions:

- Move `buildPrompt` and AI parsing out of `app.jsx` into a server endpoint.
- Replace `localStorage` as the source of truth with Supabase. Keep local draft state only for pending chat UI.
- Extract transaction/report calculations into pure functions under `frontend/src/domain/finance`.
- Convert UI components into imported modules: `Chat`, `InputBar`, `MessageBubble`, `TransactionCard`, `ReportCard`, `Dashboard`.
- Define a strict `Transaction` type and a strict `AiParseResult` type.
- Store original user messages and AI parse metadata separately from confirmed transactions if auditability matters.

## Migration Plan

### Phase 1: Stabilize the Frontend Shell

- Create a Vite React TypeScript app in the repository root.
- Move prototype files into `frontend/src/components` and `frontend/src/features/chat`.
- Replace global `window.TransactionCard`, `window.Dashboard`, and browser JSX scripts with normal imports.
- Move styles from inline objects into reusable component styles only where duplication or responsiveness requires it.
- Preserve the current visual design and workflow; avoid redesign during the migration.

### Phase 2: Make AI Parsing Production-Grade

- Add `/api/parse-transaction` or a Supabase Edge Function.
- Use schema-constrained output for:
  - `isTransaction`
  - `isReport`
  - `transaction.type`
  - `transaction.amount`
  - `transaction.category`
  - `transaction.description`
  - `transaction.date`
  - `message`
- Validate the model response with Zod before the frontend sees it.
- Add deterministic fallback rules for common simple entries like `spent 12 on lunch`.
- Log parse failures without storing sensitive raw text longer than needed.

### Phase 3: Add Real Persistence

- Add Supabase Auth.
- Create tables:
  - `transactions`
  - `transaction_messages` or `chat_messages`
  - `categories`
  - `user_preferences`
- Enable RLS on all user data tables.
- Add migration scripts and seed categories.
- Replace `localStorage` persistence with authenticated database reads/writes.

### Phase 4: Ship MVP Quality

- Add loading, empty, error, offline, and retry states.
- Add transaction edit/delete after save.
- Add import/export as CSV.
- Add Playwright coverage for the main workflow.
- Add privacy controls: delete account data, export data, clear chat history.
- Deploy the web app and API with environment-managed provider keys.

### Phase 5: Mobile Path

- Add PWA installability first if mobile demand is light.
- Move to Expo only after validating that native capabilities are worth the rewrite: push reminders, receipt capture, biometric lock, widgets, or app store distribution.

## Main Risks

- AI misclassification: Financial inputs need user confirmation and strict validation. The current confirm-card flow is good; keep it.
- Privacy and trust: Do not send more history to the model than needed. Summarize context where possible.
- Data ownership: Database policies must be tested, not assumed.
- Cost control: Add rate limits per user and cache/report calculations locally where appropriate.
- Scope creep: Bank integrations, budgeting rules, receipt OCR, and multi-currency support should wait until the core manual-entry loop is reliable.

## Decision

Proceed with a Vite React TypeScript MVP and a secure backend AI endpoint. Use Supabase for auth and Postgres persistence. Keep Expo as a later native app path after the web MVP proves the workflow.

This path gives the best balance of speed, product quality, and security for the current prototype.
