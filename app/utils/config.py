import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    DB_DRIVER = os.environ.get('DB_DRIVER') or 'ODBC Driver 17 for SQL Server'
    DB_SERVER = os.environ.get('DB_SERVER') or '192.168.1.10'
    DB_NAME = os.environ.get('DB_NAME') or 'ticketdbreport'
    DB_USER = os.environ.get('DB_USER') or 'reportuser'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'sa@123'
    MODEL_NAME = os.environ.get('MODEL_NAME') or 'all-MiniLM-L6-v2'
    SAVE_PATH = os.environ.get('SAVE_PATH') or 'data/mapped_issues.xlsx'
    SIMILARITY_THRESHOLD = float(os.environ.get('SIMILARITY_THRESHOLD') or 0.2)
    MIN_SEARCH_SCORE = float(os.environ.get('MIN_SEARCH_SCORE') or 0.2)
    
    @property
    def DB_CONNECTION_STRING(self):
        db_params = (
            f"DRIVER={{{self.DB_DRIVER}}};"
            f"SERVER={self.DB_SERVER};"
            f"DATABASE={self.DB_NAME};"
            f"UID={self.DB_USER};"
            f"PWD={self.DB_PASSWORD}"
        )
        return f"mssql+pyodbc:///?odbc_connect={db_params}"

config = Config()