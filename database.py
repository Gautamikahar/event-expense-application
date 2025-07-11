import sqlite3

# Connect to the SQLite database
def connect():
    return sqlite3.connect("event_splitter.db")

# Initialize all required tables
def init_db():
    conn = connect()
    c = conn.cursor()

    # Create Events Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')

    # Create Members Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
        )
    ''')

    # Create Expenses Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            paid_by TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
        )
    ''')

    # Create Expense Participants Table (Many-to-Many)
    c.execute('''
        CREATE TABLE IF NOT EXISTS expense_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_id INTEGER NOT NULL,
            member_name TEXT NOT NULL,
            FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
