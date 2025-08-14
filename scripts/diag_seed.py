import sys
from pathlib import Path
# Ensure project root is on sys.path so 'app' package resolves when running from scripts/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.database.curriculum_data_loader import JSONDataLoader
from app.database.db_connection import DatabaseConnection
from app.database.db_migrations_v2 import DatabaseMigrations


def main():
    db = DatabaseConnection()
    m = DatabaseMigrations(db)
    print("ensure:", m.run_migrations())

    loader = JSONDataLoader()
    print("data_dir exists:", loader.data_dir.exists(), str(loader.data_dir))

    grades = loader.load_all_grade_files()
    print("grades loaded:", len(grades), sorted(list(grades.keys())))

    subjects = loader.extract_subjects()
    print("subjects extracted:", len(subjects))
    print("first subjects:", subjects[:5])

    units = loader.extract_units()
    print("units extracted:", len(units))
    print("first units:", units[:5])

    topics = loader.extract_topics()
    print("topics extracted:", len(topics))
    print("first topics:", topics[:5])

    grades_sql = loader.generate_grades_sql()
    print("grades_sql empty:", not bool(grades_sql))

    # Ensure grades present
    try:
        with db as conn:
            if grades_sql:
                conn.cursor.execute(grades_sql)
                conn.connection.commit()
        print("grades insert executed")
    except Exception as e:
        print("grades insert error:", repr(e))

    grade_map = loader.get_grade_id_map(db)
    print("grade_id_map:", grade_map)

    subjects_sql = loader.generate_subjects_sql(grade_map)
    print("subjects_sql empty:", not bool(subjects_sql))
    if subjects_sql:
        try:
            with db as conn:
                conn.cursor.execute(subjects_sql)
                conn.connection.commit()
            print("subjects insert executed")
        except Exception as e:
            print("subjects insert error:", repr(e))

    try:
        with db as conn:
            conn.cursor.execute("SELECT COUNT(*) AS cnt FROM subjects")
            print("subjects count in db:", conn.cursor.fetchone()['cnt'])
            conn.cursor.execute("SELECT g.grade_name, s.subject_name FROM subjects s JOIN grades g ON s.grade_id=g.grade_id ORDER BY g.grade_id, s.subject_name LIMIT 10")
            print("sample subjects:", conn.cursor.fetchall())
    except Exception as e:
        print("verify subjects error:", repr(e))

    # Insert units
    subj_map = loader.get_subject_id_map(db)
    print("subject_id_map size:", len(subj_map))
    units_sql = loader.generate_units_sql(subj_map)
    print("units_sql empty:", not bool(units_sql))
    if units_sql:
        try:
            with db as conn:
                conn.cursor.execute(units_sql)
                conn.connection.commit()
            print("units insert executed")
        except Exception as e:
            print("units insert error:", repr(e))

    # Insert topics
    unit_map = loader.get_unit_id_map(db)
    print("unit_id_map size:", len(unit_map))
    topics_sql = loader.generate_topics_sql(unit_map)
    print("topics_sql empty:", not bool(topics_sql))
    if topics_sql:
        try:
            with db as conn:
                conn.cursor.execute(topics_sql)
                conn.connection.commit()
            print("topics insert executed")
        except Exception as e:
            print("topics insert error:", repr(e))

    # Final counts
    try:
        with db as conn:
            for t in ["grades","subjects","units","topics"]:
                conn.cursor.execute(f"SELECT COUNT(*) AS cnt FROM {t}")
                print(f"{t} count:", conn.cursor.fetchone()['cnt'])
    except Exception as e:
        print("final counts error:", repr(e))


if __name__ == "__main__":
    main()
