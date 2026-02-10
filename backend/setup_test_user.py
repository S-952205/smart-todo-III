from sqlmodel import Session, select
from db import engine
from models import User
from passlib.context import CryptContext
import uuid
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def setup_test_user():
    with Session(engine) as session:
        # Check if test user exists
        test_email = "test@example.com"
        user = session.exec(select(User).where(User.email == test_email)).first()

        if user:
            print(f"Test user already exists: {test_email}")
            # Update password to known value
            user.password = pwd_context.hash("testpassword123")
            session.add(user)
            session.commit()
            print("Password updated to: testpassword123")
        else:
            # Create new test user
            new_user = User(
                id=str(uuid.uuid4()),
                email=test_email,
                name="Test User",
                password=pwd_context.hash("testpassword123"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(new_user)
            session.commit()
            print(f"Created new test user: {test_email}")
            print("Password: testpassword123")

        print(f"User ID: {user.id if user else new_user.id}")

if __name__ == "__main__":
    setup_test_user()
