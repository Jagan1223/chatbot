from app.db.session import get_connection

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS loan_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            details TEXT,
            submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

def save_loan(details: str) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO loan_applications (details) VALUES (?)", (details,))
        conn.commit()
        return cur.lastrowid