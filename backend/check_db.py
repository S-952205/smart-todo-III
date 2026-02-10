from db import engine
from sqlmodel import text
from models import Task, User
from models.chat_models import Conversation, Message

print('Testing database connection...')
with engine.connect() as conn:
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")).fetchall()
    tables = [r[0] for r in result]
    print('Tables in database:', tables)

    # Check if task table has any data
    if 'task' in tables:
        count = conn.execute(text("SELECT COUNT(*) FROM task")).fetchone()
        print(f'Number of tasks in database: {count[0]}')

    if 'user' in tables:
        count = conn.execute(text("SELECT COUNT(*) FROM user")).fetchone()
        print(f'Number of users in database: {count[0]}')
