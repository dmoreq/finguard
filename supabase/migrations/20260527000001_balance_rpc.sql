-- Aggregated balance for a user and date range (used by action_get_balance).

create or replace function get_balance_summary(
  p_user_id uuid,
  p_start date,
  p_end date
)
returns table(income numeric, expenses numeric, net numeric)
language sql
security definer
set search_path = public
as $$
  select
    coalesce(sum(case when type = 'income' then amount else 0 end), 0) as income,
    coalesce(sum(case when type = 'expense' then amount else 0 end), 0) as expenses,
    coalesce(sum(case when type = 'income' then amount
                      when type = 'expense' then -amount
                      else 0 end), 0) as net
  from transactions
  where user_id = p_user_id
    and status = 'confirmed'
    and transaction_date between p_start and p_end;
$$;

grant execute on function get_balance_summary(uuid, date, date) to service_role;
