from db import engine
from sqlmodel import text

with engine.connect() as conn:
    result = conn.execute(text('SELECT email, id FROM "user" LIMIT 1')).fetchone()
    if result:
        print(f'Email: {result[0]}')
        print(f'ID: {result[1]}')
    else:
        print('No users found')
