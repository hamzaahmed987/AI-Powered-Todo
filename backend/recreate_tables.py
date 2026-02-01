"""Recreate all database tables."""
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from app.database.session import engine
from app.models.base import Base
from app.models.user import User
from app.models.task import Task
from app.models.task_share import TaskShare

print("Dropping all tables with CASCADE...")
with engine.connect() as conn:
    conn.execute(text("DROP SCHEMA public CASCADE"))
    conn.execute(text("CREATE SCHEMA public"))
    conn.commit()

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Done! Tables recreated successfully.")
