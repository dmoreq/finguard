# Backend query audit (BE-1)

All functions in `actions/db/queries.py` scope by `user_id` (or derive it from the caller).

| Function | Table | `user_id` filter |
|----------|-------|------------------|
| `insert_transaction` | transactions | In `TransactionInsert.user_id` |
| `get_spending_by_category` | transactions | `.eq("user_id", user_id)` |
| `get_balance_summary` | RPC | `p_user_id` argument |
| `list_transactions` | transactions | `.eq("user_id", user_id)` |
| `get_latest_pending_transaction` | transactions | `.eq("user_id", user_id)` |
| `get_transaction` | transactions | `.eq("user_id", user_id)` |
| `delete_transaction` | transactions | `.eq("user_id", user_id)` |
| `update_transaction` | transactions | `.eq("user_id", user_id)` |
| `confirm_transaction` | transactions | `.eq("user_id", user_id)` |

**Session start** loads `profiles` with `.eq("id", user_id)` where `user_id` comes from webhook metadata or `sender_id`.

**Rule:** Never add a query without `user_id` (or primary key + `user_id`) in the WHERE clause.
