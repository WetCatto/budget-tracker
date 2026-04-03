# Budget Tracker

A local, offline terminal budget tracker built with Python and Textual.

All data is stored in `~/.budget_tracker.db` (SQLite) — nothing leaves your machine.

## Setup

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## Running

```bash
venv/bin/python main.py
```

## Navigation

| Key | Action |
|-----|--------|
| `1` | Dashboard |
| `2` | Transactions |
| `3` | Monthly Summary |
| `4` | Charts |
| `5` | Budgets |
| `a` | Add transaction (any screen) |
| `e` | Edit selected row |
| `d` | Delete selected row |
| `[` / `]` | Previous / next month |
| `n` | Add budget limit (Budgets screen) |
| `q` | Quit |

## Screens

**Dashboard** — current month balance, budget warnings, and your 10 most recent transactions.

**Transactions** — full transaction list filterable by month. Use `[` and `]` to move between months, `e` to edit a selected row, `d` to delete.

**Monthly Summary** — income, spending, and budget limits broken down by category with a net total. Navigate months with `[` and `]`.

**Charts** — spending by category (current month) and expenses over the last 6 months, rendered as bar charts in the terminal.

**Budgets** — set monthly spending limits per category. Over-budget categories appear as warnings on the Dashboard. Press `n` to add a limit, `e` to edit, `d` to delete.

## Transactions

- **Positive amounts** are income (e.g. `2000` for salary)
- **Negative amounts** are expenses (e.g. `-45.50` for groceries)
- Categories are free-form text — type anything (Food, Rent, Income, etc.)
