from sqlalchemy import create_engine, text
from app.env_variables import DB_USER, DB_PASS, DB_HOST, DB_PORT


class SQLOperations:

    def __init__(self, database):
        server = f'{DB_HOST}:{DB_PORT}' if DB_PORT else DB_HOST
        # Add more connection parameters and use TCP explicitly
        self.connection_string = (
            f"mssql+pyodbc://{DB_USER}:{DB_PASS}@{server}/{database}"
            "?driver=ODBC+Driver+18+for+SQL+Server"
            "&TrustServerCertificate=yes"
            "&encrypt=yes"
            "&timeout=30"
            "&connection_timeout=30"
            "&trusted_connection=no"
            "&Mars_Connection=yes"
        )
        # Add echo=True to see the SQL queries for debugging
        self.engine = create_engine(self.connection_string, echo=True)

    def execute_simple_select(self, fields: str, table: str, conditions: str):
        return self.execute_query(f'SELECT {fields} FROM {table} WHERE {conditions}')

    def execute_query(self, query, params=None):
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            return [dict(row) for row in result.fetchall()]

    def execute_simple_insert(self, table: str, columns: str, values: str):
        return self.execute_non_query(f'INSERT INTO {table} ({columns}) VALUES ({values})')

    def execute_non_query(self, query, params=None):
        with self.engine.connect() as conn:
            conn.execute(text(query), params)

