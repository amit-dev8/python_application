from sqlalchemy import text

from src.utils.db import engine


with engine.connect() as connection:
    version = connection.execute(text("SELECT version()"))
    print("Database connected successfully!")
    print(version.scalar_one())
