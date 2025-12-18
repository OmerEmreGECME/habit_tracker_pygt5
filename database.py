import sqlite3
import datetime

DB_FILENAME = "habit_tracker.db"

class Database:
    def __init__(self, db_file=DB_FILENAME):
        self.conn = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            total_points INTEGER DEFAULT 0
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT COLLATE NOCASE,
            category TEXT,
            frequency TEXT,
            created_at DATE,
            UNIQUE(user_id, name),
            FOREIGN KEY(user_id) REFERENCES users(id)
);
""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER,
            date DATE,
            UNIQUE(habit_id, date),
            FOREIGN KEY(habit_id) REFERENCES habits(id)
        );
        """)
             
        self.conn.commit()
        
    # ---------------------------
    # User methods
    # ---------------------------
    def create_user(self, username, email, password_hash):
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                        (username, email, password_hash))
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_user_by_email(self, email):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        return cur.fetchone()

    def get_user_by_id(self, user_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cur.fetchone()

    def add_points(self, user_id, points):
        cur = self.conn.cursor()
        cur.execute("UPDATE users SET total_points = total_points + ? WHERE id = ?", (points, user_id))
        self.conn.commit()

    def total_points(self, user_id):
        cur = self.conn.cursor()
        cur.execute("SELECT total_points FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        return row["total_points"] if row else 0

    # ---------------------------
    # Habit methods
    # ---------------------------
    def add_habit(self, user_id, name, category, frequency):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO habits (user_id, name, category, frequency, created_at) VALUES (?, ?, ?, ?, ?)",
                    (user_id, name, category, frequency, datetime.date.today()))
        self.conn.commit()
        return cur.lastrowid

    def update_habit(self, habit_id, name, category, frequency):
        cur = self.conn.cursor()
        cur.execute("UPDATE habits SET name = ?, category = ?, frequency = ? WHERE id = ?",
                    (name, category, frequency, habit_id))
        self.conn.commit()

    def delete_habit(self, habit_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))
        cur.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        self.conn.commit()

    def list_habits(self, user_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM habits WHERE user_id = ?", (user_id,))
        return cur.fetchall()

    def get_habit(self, habit_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
        return cur.fetchone()

    # ---------------------------
    # Completion methods
    # ---------------------------
    def completion_count_for_habit(self, habit_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM completions WHERE habit_id = ?",
            (habit_id,)
        )
        row = cur.fetchone()
        return row["cnt"] if row else 0
     
    def mark_completed(self, habit_id, date_):
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO completions (habit_id, date) VALUES (?, ?)", (habit_id, date_))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def unmark_completed(self, habit_id, date_):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM completions WHERE habit_id = ? AND date = ?", (habit_id, date_))
        self.conn.commit()

    def is_completed(self, habit_id, date_):
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM completions WHERE habit_id = ? AND date = ?", (habit_id, date_))
        return cur.fetchone() is not None

    def completions_for_habit(self, habit_id):
        cur = self.conn.cursor()
        cur.execute("SELECT date FROM completions WHERE habit_id = ? ORDER BY date", (habit_id,))
        return [r["date"] for r in cur.fetchall()]
    
    
