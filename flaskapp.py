from flask import Flask, jsonify, request, redirect, url_for, render_template_string
from collections import Counter
import sqlite3
import os

app = Flask(__name__)

DATABASE = os.path.join(os.path.dirname(__file__), 'mydatabase.db')

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Ensure it returns dict-like rows
    return conn

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/countme/<input_str>')
def count_me(input_str):
    input_ctr = Counter(input_str)
    response = []
    for l, ct in input_ctr.most_common():
        response.append('"{}": {}'.format(l, ct))
    return '<br>'.join(response)

# Route to display a form to enter username, password, and email
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # If first and last names are provided, update the user record
        if 'first_name' in request.form and 'last_name' in request.form:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']  # Email from previous step
            
            # Check for empty inputs
            if not first_name or not last_name or not email:
                return render_template_string('''
                    <h1>Enter Your Name</h1>
                    <p style="color: red;">All fields are required.</p>
                    <form method="POST">
                        <input type="hidden" name="email" value="{{ email }}">
                        <label for="first_name">First Name:</label><br>
                        <input type="text" id="first_name" name="first_name"><br>
                        <label for="last_name">Last Name:</label><br>
                        <input type="text" id="last_name" name="last_name"><br><br>
                        <input type="submit" value="Submit">
                    </form>
                ''', email=email)

            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Update the user's first and last name
                cursor.execute("UPDATE users SET firstname = ?, lastname = ? WHERE email = ?", 
                               (first_name, last_name, email))
                conn.commit()
                conn.close()
                
                return redirect(url_for('search'))

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        # Handle the initial registration (username, password, email)
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Check for empty inputs
        if not username or not password or not email:
            return render_template_string('''
                <h1>Register</h1>
                <p style="color: red;">All fields are required.</p>
                <form method="POST" action="/register">
                    <label for="username">Username:</label><br>
                    <input type="text" id="username" name="username"><br>
                    <label for="password">Password:</label><br>
                    <input type="password" id="password" name="password"><br>
                    <label for="email">Email:</label><br>
                    <input type="email" id="email" name="email"><br><br>
                    <input type="submit" value="Register">
                </form>
            ''')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert new user data into the database
            cursor.execute('''INSERT INTO users (username, password, email) VALUES (?, ?, ?)''',
                           (username, password, email))

            conn.commit()
            conn.close()

            # Render the form for entering first and last name
            return render_template_string('''<h1>Enter Your Name</h1>
                <p>Almost done! Please help us get to know you better by entering
                your name.</p>
                <form method="POST">
                    <input type="hidden" name="email" value="{{ email }}">
                    <label for="first_name">First Name:</label><br>
                    <input type="text" id="first_name" name="first_name"><br>
                    <label for="last_name">Last Name:</label><br>
                    <input type="text" id="last_name" name="last_name"><br><br>
                    <input type="submit" value="Submit">
                </form>
            ''', email=email)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Render the initial registration form
    return '''
        <form method="POST" action="/register">
            <h1>Register</h1>
            <p>Please enter a username, password, and email address to register.
            Click register when you're ready to move on.</p>
            <label for="username">Username:</label><br>
            <input type="text" id="username" name="username"><br>
            <label for="password">Password:</label><br>
            <input type="password" id="password" name="password"><br>
            <label for="email">Email:</label><br>
            <input type="email" id="email" name="email"><br><br>
            <input type="submit" value="Register">
        </form>
    '''

# Route for user search
@app.route('/search', methods=['GET', 'POST'])
def search():
    error_message = None  # Initialize error message
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check for empty inputs
        if not username or not password:
            error_message = 'Both fields are required.'

        else:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()

                # Check if the username and password match
                cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
                user = cursor.fetchone()

                conn.close()

                if user:
                    # Render user profile
                    return render_template_string('''
                        <h1>Your Profile</h1>
                        <p>Username: {{ username }}</p>
                        <p>Email: {{ email }}</p>
                        <p>First Name: {{ first_name }}</p>
                        <p>Last Name: {{ last_name }}</p>
                    ''', username=user['username'], email=user['email'], 
                    first_name=user['firstname'], last_name=user['lastname'])

                else:
                    error_message = 'Invalid username or password. Please try again.'

            except Exception as e:
                return jsonify({"error": str(e)}), 500

    # Render the search form, including any error message
    return render_template_string('''
        <form method="POST" action="/search">
            <h1>Get Profile</h1>
            <p>Authenticate to see your profile information. Invalid usernames
            and/or passwords will be rejected.</p>
            {% if error_message %}
                <p style="color: red;">{{ error_message }}</p>
            {% endif %}
            <label for="username">Username:</label><br>
            <input type="text" id="username" name="username"><br>
            <label for="password">Password:</label><br>
            <input type="password" id="password" name="password"><br><br>
            <input type="submit" value="Search">
        </form>
    ''', error_message=error_message)

# Route to get all users data as JSON
@app.route('/getusers')
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users;")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]

        users = [dict(zip(column_names, row)) for row in rows]
        conn.close()

        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
