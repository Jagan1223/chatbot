from app.db.session import get_connection

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS loan_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                details TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'SUBMITTED',
                submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_loan(user_id: str, details: str, status: str = "SUBMITTED") -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO loan_applications (user_id, details, status)
            VALUES (?, ?, ?)
            """,
            (user_id, details, status),
        )
        conn.commit()
        return cur.lastrowid
    
def get_loans_by_user(user_id: str) -> list[dict]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, details, status, submission_date
            FROM loan_applications
            WHERE user_id = ?
            ORDER BY submission_date DESC
            """,
            (user_id,),
        )

        rows = cur.fetchall()

        return [
            {
                "loan_id": f"sub{row[0]:07d}",
                "details": row[1],
                "status": row[2],
                "submission_date": row[3],
            }
            for row in rows
        ]
