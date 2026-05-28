# Backend query audit

All functions in `actions/db/queries.py` must scope by `user_id` (or derive it from the authenticated caller).

| Function | Table | `user_id` filter |
|----------|-------|------------------|
| `insert_transaction` | transactions | `TransactionInsert.user_id` |
| `get_spending_by_category` | transactions | `WHERE user_id = ?` |
| `get_balance_summary` | transactions | `WHERE user_id = ?` |
| `list_transactions` | transactions | `WHERE user_id = ?` |
| `get_latest_pending_transaction` | transactions | `WHERE user_id = ?` |
| `get_transaction` | transactions | `WHERE user_id = ?` |
| `delete_transaction` | transactions | `WHERE user_id = ?` |
| `update_transaction` | transactions | `WHERE user_id = ?` |
| `get_profile` / `update_profile` | profiles | `WHERE id = ?` (profile id = user id) |

**Rule:** Never add a query without `user_id` in the WHERE clause for user-owned rows.

**Chat:** `load_user_profile` in `actions/services/profile.py` reads profile by `user_id` from webhook metadata.
