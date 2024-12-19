from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Get the port from the environment variable (default to 5000 if not set)
port = int(os.environ.get("PORT", 5000))

# Get the database connection details from environment variables
db_url = os.environ.get("DATABASE_URL")  # Set this in Render's environment variables
if db_url:
    conn = psycopg2.connect(db_url, sslmode='require')  # Add sslmode for secure connection
else:
    conn = None

@app.route('/')
def hello():
    return "Hello, world!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

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

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            cur.close()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error: Username might already exist.', 'danger')

    return render_template('login.html')

@app.route('/welcome')
def welcome():
    # Page for "Merry Christmas" message
    return render_template('welcome.html')

if __name__ == '__main__':
    app.run(debug=True)
