import os
from sqlalchemy.engine.url import URL

def get_database_url():
    """Get database URL from environment variables"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        database_url = str(URL.create(
            drivername="postgresql",
            username=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            database=os.getenv("POSTGRES_DB"),
        ))
    return database_url
