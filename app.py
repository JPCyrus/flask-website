from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Get the port from the environment variable (default to 5000 if not set)
port = int(os.environ.get("PORT", 5000))

# Get the database connection URL from environment variables
db_url = os.environ.get("DATABASE_URL")  # Set this in Render's environment variables

# Establish a secure database connection using DATABASE_URL
if db_url:
    conn = psycopg2.connect(db_url, sslmode='require')  # SSL mode required for Render's PostgreSQL service
else:
    conn = None  # You can handle this case or use a fallback database if needed

@app.route('/')
def hello():
    return "Hello, world!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if conn:
            try:
                # Query database
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                user = cur.fetchone()
                cur.close()

                if user:
                    flash('Login successful!', 'success')
                    return redirect(url_for('welcome'))  # Redirect to the Christmas greeting page
                else:
                    flash('Invalid credentials', 'danger')
            except Exception as e:
                flash(f"Database error: {e}", 'danger')
        else:
            flash("Database connection error", 'danger')

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
        else:
            flash("Database connection error", 'danger')

    return render_template('login.html')

@app.route('/welcome')
def welcome():
    # Page for "Merry Christmas" message
    return render_template('welcome.html')

if __name__ == '__main__':
    # Ensure Flask listens on 0.0.0.0 to be accessible externally
    app.run(host="0.0.0.0", port=port, debug=True)
