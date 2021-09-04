import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# My Function to check a database connection.
def check_db_connection():
    try:
        conLink = get_db_connection()
        conLink.close()
    except:
        raise Exception("Failure.... in the Database Connection")

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# My Function to check posts table existance.
def check_posts_table():
    try:
        conLink = get_db_connection()
        conLink.execute('select 1 from posts').fetchone()
        conLink.close()
    except:
        raise Exception("Error...posts table does not exist")

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

"""Define the Healthcheck endpoint with the following response:
An HTTP 200 status code
A JSON response containing the result: OK - healthy message"""
@app.route('/healthz', methods=['GET'])
def healthz():
    status_code = 200
    response_body = {'result' : 'OK - healthy'}
    
    try:
        check_db_connection()
        check_posts_table()

    except Exception as excp:
        status_code = 500
        response_body = {'result': 'ERROR - unhealthy'}
        response_body['description'] = str(excp)

    response = app.response_class(
                                     status = status_code,
                                     response = json.dumps(response_body),
                                     mimetype = 'application/json'
                                 )

    return response


# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
