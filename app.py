from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
import os
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Get the port from the environment variable (default to 5000 if not set)
port = int(os.environ.get("PORT", 5000))

# Get the database connection URL from environment variables
db_url = os.environ.get("DATABASE_URL")  # This should be set in Render's environment variables

if db_url:
    try:
        # Parse the database URL using urllib.parse
        url = urlparse(db_url)

        # Extract the necessary components from the parsed URL
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port

        # Establish a secure database connection using the URL details
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            sslmode='require'  # SSL mode required by Render's PostgreSQL service
        )
        print("Database connection established successfully.")
    except Exception as e:
        print(f"Error: Unable to connect to the database. {e}")
        conn = None  # Set conn to None if the connection fails
else:
    print("Error: DATABASE_URL is not set.")
    conn = None  # Handle this case if DATABASE_URL is not set


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('welcome'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if conn:
            try:
                # Query database for user credentials
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                user = cur.fetchone()
                cur.close()

                if user:
                    session['user_id'] = user[0]  # Store user ID in session
                    flash('Login successful!', 'success')
                    return redirect(url_for('welcome'))
                else:
                    flash('Invalid credentials', 'danger')
            except Exception as e:
                flash(f"Database error: {e}", 'danger')
                print(f"Database query error: {e}")
        else:
            flash("Database connection error", 'danger')
            print("Database connection error")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if conn:
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                conn.commit()
                cur.close()
                flash('Registration successful!', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f'Error: {e}', 'danger')
                print(f"Error during registration: {e}")
        else:
            flash("Database connection error", 'danger')
            print("Database connection error")

    return render_template('register.html')  # Make sure you create a register.html template


@app.route('/welcome')
def welcome():
    if 'user_id' not in session:
        flash('You need to log in first', 'warning')
        return redirect(url_for('login'))
    return render_template('welcome.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))  # Redirect to homepage


if __name__ == '__main__':
    # Ensure Flask listens on 0.0.0.0 to be accessible externally
    app.run(host="0.0.0.0", port=port, debug=True)
