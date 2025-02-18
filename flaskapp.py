from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for session management

DATABASE = '/var/www/html/flaskapp/users.db'

# Ensure database and table exist
if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    firstname TEXT NOT NULL,
                    lastname TEXT NOT NULL,
                    email TEXT NOT NULL,
                    address TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return redirect(url_for('login'))  # Show login page first

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        address = request.form['address']

        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, firstname, lastname, email, address) VALUES (?, ?, ?, ?, ?, ?)",
                      (username, password, firstname, lastname, email, address))
            conn.commit()
            conn.close()

            session['username'] = username  # Store session
            return redirect(url_for('profile', username=username))  # Redirect to profile
        except sqlite3.IntegrityError:
            return "Error: Username already exists!"

    return render_template('register.html')

@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT firstname, lastname, email, address FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    if user:
        return render_template('profile.html', user=user)
    else:
        return "User not found!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('profile', username=username))
        else:
            return "Invalid username or password"

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
