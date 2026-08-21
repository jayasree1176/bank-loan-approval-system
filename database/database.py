import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database.db'))
SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'schema.sql'))

def get_db_connection():
    """Establish and return SQLite database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database using schema.sql."""
    conn = get_db_connection()
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    """Execute SQL query and return dict row results."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Execute INSERT/UPDATE/DELETE query and return lastrowid."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id
