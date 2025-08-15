import sys
from pathlib import Path
import argparse

# Ensure project root is on sys.path so 'app' package resolves when running from scripts/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database.db_connection import DatabaseConnection
from app.database.db_migrations_v2 import DatabaseMigrations


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Database migration utilities")
    parser.add_argument(
        "--force-recreate",
        action="store_true",
        help="Drop all managed tables and recreate them (DANGER in prod)",
    )
    parser.add_argument(
        "--indexes",
        action="store_true",
        help="Create missing performance indexes after ensuring tables exist",
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Confirm dangerous operations without prompting",
    )
    args = parser.parse_args(argv)

    db = DatabaseConnection()
    migrations = DatabaseMigrations(db)

    ok_tables: bool
    if args.force_recreate and not args.yes:
        print("WARNING: --force-recreate will DROP and RECREATE all managed tables. This will DELETE data.")
        try:
            resp = input("Type 'yes' to continue: ").strip().lower()
        except EOFError:
            resp = ""
        if resp != "yes":
            print("Aborted.")
            return 2
    if args.force_recreate:
        ok_tables = migrations.force_recreate()
    else:
        ok_tables = migrations.run_migrations()

    print(f"tables_ok: {ok_tables}")

    ok_idx = True
    if args.indexes:
        ok_idx = migrations.create_missing_indexes()
        print(f"indexes_ok: {ok_idx}")

    return 0 if (ok_tables and ok_idx) else 1


if __name__ == "__main__":
    sys.exit(main())
