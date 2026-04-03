import sys


def cli():
    """
    Simple CLI for adding transactions without opening the TUI.

    Usage:
        budget add <description> <amount> [category]

    Examples:
        budget add Rent -12000 Rent
        budget add Salary +45000 Income
        budget add Coffee -150
    """
    args = sys.argv[1:]

    if not args or args[0] != "add":
        # Launch TUI — init DB first so all tables exist before widgets mount
        import db as _db
        _db.init_db()
        from app import BudgetApp
        BudgetApp().run()
        return

    # budget add <description> <amount> [category]
    if len(args) < 3:
        print("Usage: budget add <description> <amount> [category]")
        print("  e.g. budget add Rent -12000 Rent")
        sys.exit(1)

    description = args[1]
    amount_str = args[2]
    category = args[3] if len(args) >= 4 else "Uncategorized"

    try:
        amount = float(amount_str.lstrip("+"))
    except ValueError:
        print(f"Error: '{amount_str}' is not a valid amount. Use e.g. -150 or +45000")
        sys.exit(1)

    from datetime import date
    import db

    db.init_db()
    today = date.today().isoformat()
    db.add_transaction(today, description, amount, category)

    symbol = "₱"
    sign = "+" if amount >= 0 else ""
    print(f"Added: {description}  {sign}{symbol}{amount:,.2f}  [{category}]  {today}")


if __name__ == "__main__":
    cli()
