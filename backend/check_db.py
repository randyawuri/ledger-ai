from sqlalchemy import text
from app.db.session import engine

with engine.connect() as conn:
    result = conn.scalar(text("SELECT 1"))
    print(result)