-- SEC-5: Ensure balance RPC is not callable by anon/authenticated clients.

revoke all on function get_balance_summary(uuid, date, date) from public;
revoke all on function get_balance_summary(uuid, date, date) from anon;
revoke all on function get_balance_summary(uuid, date, date) from authenticated;

grant execute on function get_balance_summary(uuid, date, date) to service_role;
