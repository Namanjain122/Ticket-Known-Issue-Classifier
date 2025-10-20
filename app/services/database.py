import pandas as pd
from sqlalchemy import create_engine, text
from ..utils.config import config

class DatabaseService:
    def __init__(self):
        self.engine = create_engine(config.DB_CONNECTION_STRING)
    
    def get_known_issues(self):
        sql = "SELECT id, ticketType, name FROM dbo.Known_Issue WHERE name IS NOT NULL"
        with self.engine.connect() as conn:
            df = pd.read_sql(sql, conn)
        return df[['id', 'name', 'ticketType']].dropna().values.tolist()
    
    def is_connected(self):
        """Check if database connection is alive using SQLAlchemy"""
        try:
            # Try to execute a simple query using SQLAlchemy
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()  # Try to fetch a result
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")  # For debugging
            return False
        
db_service = DatabaseService()