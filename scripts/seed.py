import sys
from pathlib import Path
import argparse

# Ensure project root is on sys.path so 'app' package resolves when running from scripts/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database.db_connection import DatabaseConnection
from app.database.db_migrations_v2 import DatabaseMigrations

DEFAULT_QUESTIONS_DIR = 'app/data/quiz_banks'


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Database seeding utilities")
    parser.add_argument(
        "--curriculum",
        action="store_true",
        help="Seed grades/subjects/units/topics from JSON files",
    )
    parser.add_argument(
        "--questions",
        action="store_true",
        help="Seed questions and options from JSON files",
    )
    parser.add_argument(
        "--file",
        dest="file",
        default=None,
        help="Path to a single question JSON file to seed",
    )
    parser.add_argument(
        "--users",
        action="store_true",
        help="Seed default development users (admin/demo/test)",
    )
    parser.add_argument(
        "--dir",
        dest="directory",
        default=None,
        help=f"Directory for question JSON files (default: {DEFAULT_QUESTIONS_DIR})",
    )
    parser.add_argument(
        "--no-ensure",
        action="store_true",
        help="Skip ensuring tables exist before seeding",
    )

    args = parser.parse_args(argv)

    # If no category flags provided, default to curriculum + questions only
    any_selected = args.curriculum or args.questions or args.users
    do_curriculum = args.curriculum or (not any_selected)
    do_questions = args.questions or (not any_selected)
    do_users = args.users  # only when explicitly requested

    db = DatabaseConnection()
    migrations = DatabaseMigrations(db)

    if not args.no_ensure:
        migrations.run_migrations()

    overall_ok = True

    if do_curriculum:
        ok_curr_all = migrations.seed_initial_data()
        overall_ok = overall_ok and ok_curr_all
        print(f"seed initial curriculum (grades+subjects+units+topics): {ok_curr_all}")

    if do_questions:
        if args.file:
            success, total = migrations.seed_questions_file(args.file)
            print(f"seed questions file '{args.file}': {success}/{total} inserted")
            overall_ok = overall_ok and (success >= 0)
        else:
            directory = args.directory or DEFAULT_QUESTIONS_DIR
            results = migrations.seed_questions_from_dir(directory)
            total_success = sum((s for (s, t) in results.values()), 0)
            total_questions = sum((t for (s, t) in results.values()), 0)
            print(f"seed questions from '{directory}': {total_success}/{total_questions} inserted")
            overall_ok = overall_ok and (total_success >= 0)  # not strictly failure-driven

    if do_users:
        ok_users = migrations.seed_default_users()
        print(f"seed default users: {ok_users}")
        overall_ok = overall_ok and ok_users

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
