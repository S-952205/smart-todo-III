"""
Database cleanup script to fix corrupted task priority and status values
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment")
    sys.exit(1)

# Create engine
engine = create_engine(DATABASE_URL)

print("Connecting to database...")

with engine.connect() as conn:
    # Start transaction
    trans = conn.begin()

    try:
        # Check for corrupted priority values
        print("\nChecking for corrupted priority values...")
        result = conn.execute(text("""
            SELECT id, title, priority, status
            FROM task
            WHERE priority NOT IN ('low', 'medium', 'high')
            OR status NOT IN ('todo', 'in-progress', 'done')
        """))

        corrupted_tasks = result.fetchall()

        if corrupted_tasks:
            print(f"Found {len(corrupted_tasks)} corrupted tasks:")
            for task in corrupted_tasks:
                print(f"  Task ID {task[0]}: '{task[1]}' - priority='{task[2]}', status='{task[3]}'")

            # Fix corrupted priority values
            print("\nFixing corrupted priority values...")

            # Fix 'high, ' -> 'high'
            result = conn.execute(text("""
                UPDATE task
                SET priority = 'high'
                WHERE priority LIKE 'high%' AND priority != 'high'
            """))
            print(f"  Fixed {result.rowcount} tasks with 'high*' priority")

            # Fix 'medium, ' -> 'medium'
            result = conn.execute(text("""
                UPDATE task
                SET priority = 'medium'
                WHERE priority LIKE 'medium%' AND priority != 'medium'
            """))
            print(f"  Fixed {result.rowcount} tasks with 'medium*' priority")

            # Fix 'low, ' -> 'low'
            result = conn.execute(text("""
                UPDATE task
                SET priority = 'low'
                WHERE priority LIKE 'low%' AND priority != 'low'
            """))
            print(f"  Fixed {result.rowcount} tasks with 'low*' priority")

            # Fix corrupted status values
            print("\nFixing corrupted status values...")

            # Fix 'done, ' -> 'done'
            result = conn.execute(text("""
                UPDATE task
                SET status = 'done'
                WHERE status LIKE 'done%' AND status != 'done'
            """))
            print(f"  Fixed {result.rowcount} tasks with 'done*' status")

            # Fix 'in-progress, ' -> 'in-progress'
            result = conn.execute(text("""
                UPDATE task
                SET status = 'in-progress'
                WHERE status LIKE 'in-progress%' AND status != 'in-progress'
            """))
            print(f"  Fixed {result.rowcount} tasks with 'in-progress*' status")

            # Fix 'todo, ' -> 'todo'
            result = conn.execute(text("""
                UPDATE task
                SET status = 'todo'
                WHERE status LIKE 'todo%' AND status != 'todo'
            """))
            print(f"  Fixed {result.rowcount} tasks with 'todo*' status")

            # Commit transaction
            trans.commit()
            print("\n[SUCCESS] Database cleanup completed successfully!")

        else:
            print("[OK] No corrupted tasks found!")
            trans.rollback()

    except Exception as e:
        trans.rollback()
        print(f"\n[ERROR] Error during cleanup: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

print("\nVerifying cleanup...")
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN priority NOT IN ('low', 'medium', 'high') THEN 1 ELSE 0 END) as bad_priority,
               SUM(CASE WHEN status NOT IN ('todo', 'in-progress', 'done') THEN 1 ELSE 0 END) as bad_status
        FROM task
    """))

    row = result.fetchone()
    print(f"Total tasks: {row[0]}")
    print(f"Tasks with invalid priority: {row[1]}")
    print(f"Tasks with invalid status: {row[2]}")

    if row[1] == 0 and row[2] == 0:
        print("\n[SUCCESS] All tasks have valid priority and status values!")
    else:
        print("\n[WARNING] Some tasks still have invalid values. Manual intervention may be needed.")
