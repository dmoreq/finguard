create type transaction_type as enum ('income', 'expense', 'pending');

create table profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  currency text not null default 'USD',
  timezone text not null default 'UTC',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
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

alter table profiles enable row level security;
alter table transactions enable row level security;
alter table chat_messages enable row level security;

create policy "profiles are user-owned"
on profiles for all
using (auth.uid() = id)
with check (auth.uid() = id);

create policy "transactions are user-owned"
on transactions for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create policy "chat messages are user-owned"
on chat_messages for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create index transactions_user_date_idx on transactions (user_id, transaction_date desc);
create index chat_messages_user_created_idx on chat_messages (user_id, created_at desc);
