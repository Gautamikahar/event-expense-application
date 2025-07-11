from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DATABASE = 'event_splitter.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        date TEXT,
        user_id INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        event_id INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        amount REAL,
        paid_by TEXT,
        event_id INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS expense_participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_id INTEGER,
        member_name TEXT
    )''')

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("Registered successfully!", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists", "danger")

    return render_template('register.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM events WHERE user_id=?", (session['user_id'],))
    events = c.fetchall()
    return render_template('home.html', events=events)

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        members = request.form['members'].split(',')

        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO events (name, date, user_id) VALUES (?, ?, ?)", (name, date, session['user_id']))
        event_id = c.lastrowid

        for member in members:
            c.execute("INSERT INTO members (name, event_id) VALUES (?, ?)", (member.strip(), event_id))

        conn.commit()
        flash("Event created successfully!", "success")
        return redirect(url_for('home'))

    return render_template('create_event.html')

@app.route('/select_event_for_expense', methods=['GET', 'POST'])
def select_event_for_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM events WHERE user_id=?", (session['user_id'],))
    events = c.fetchall()

    if request.method == 'POST':
        event_id = request.form['event_id']
        return redirect(url_for('add_expense', event_id=event_id))

    return render_template('select_event_for_expense.html', events=events)

@app.route('/add_expense/<int:event_id>', methods=['GET', 'POST'])
def add_expense(event_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM events WHERE id=? AND user_id=?", (event_id, session['user_id']))
    event = c.fetchone()

    if not event:
        flash("Event not found or unauthorized access.", "danger")
        return redirect(url_for('home'))

    c.execute("SELECT name FROM members WHERE event_id=?", (event_id,))
    members = [row['name'] for row in c.fetchall()]

    if request.method == 'POST':
        expense_type = request.form['type']
        amount = float(request.form['amount'])
        paid_by = request.form['paid_by']
        participants = request.form.getlist('participants')

        c.execute("INSERT INTO expenses (type, amount, paid_by, event_id) VALUES (?, ?, ?, ?)",
                  (expense_type, amount, paid_by, event_id))
        expense_id = c.lastrowid

        for participant in participants:
            c.execute("INSERT INTO expense_participants (expense_id, member_name) VALUES (?, ?)",
                      (expense_id, participant))

        conn.commit()
        flash("Expense added successfully!", "success")
        return redirect(url_for('home'))

    return render_template('add_expense.html', event=event, members=members)

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM events WHERE id=? AND user_id=?", (event_id, session['user_id']))
    event = c.fetchone()

    if not event:
        flash("Event not found or unauthorized access.", "danger")
        return redirect(url_for('home'))

    c.execute("SELECT * FROM members WHERE event_id=?", (event_id,))
    members = c.fetchall()

    c.execute("SELECT * FROM expenses WHERE event_id=?", (event_id,))
    expenses = c.fetchall()

    return render_template("event_detail.html", event=event, members=members, expenses=expenses)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
