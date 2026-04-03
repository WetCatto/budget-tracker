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

## Controls

The controls bar at the bottom of the app shows all available keys at a glance.

| Key | Action |
|-----|--------|
| `1`–`5` | Switch tabs |
| `a` | Add transaction (any screen) |
| `e` | Edit selected row |
| `d` | Delete selected row |
| `[` / `]` | Previous / next month |
| `n` | Add budget limit (Budgets screen) |
| `q` | Quit |

In the add/edit form, press **Enter** to advance to the next field. On the last field, Enter saves the transaction.

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
