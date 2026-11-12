import os
import sqlite3
from pathlib import Path
from flask import g, current_app

def get_db_path():
    """Retrieve configured database path."""
    if current_app:
        return current_app.config.get("DATABASE_PATH", "database/placement_system.db")
    return os.environ.get("DATABASE_PATH", "database/placement_system.db")

def get_db():
    """Open a unique database connection for the current application context."""
    if "db" not in g:
        db_path = get_db_path()
        if db_path != ":memory:":
            db_file = Path(db_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)
            g.db = sqlite3.connect(str(db_file))
        else:
            g.db = sqlite3.connect(":memory:")
            
        g.db.row_factory = sqlite3.Row
        # Crucial: enable foreign key support in SQLite
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db(app=None):
    """Initialize database tables using schema.sql."""
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    if app is not None:
        with app.app_context():
            db = get_db()
            db.executescript(schema_sql)
            db.commit()
    else:
        db = get_db()
        db.executescript(schema_sql)
        db.commit()

def query_db(query, args=(), one=False):
    """Execute a read query and return dict-like rows."""
    db = get_db()
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=(), commit=True):
    """Execute an INSERT/UPDATE/DELETE query and return the last row ID or affected rows."""
    db = get_db()
    cur = db.execute(query, args)
    if commit:
        db.commit()
    last_id = cur.lastrowid
    rowcount = cur.rowcount
    cur.close()
    return last_id if last_id else rowcount
