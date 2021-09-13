import sqlite3
import logging
import os

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

connCounter = 0
# My Function to count the article and ++ number of used connections.
def get_article_count(metricsObject):
    conLink = get_db_connection()
    articleCounter = conLink.execute('select count(*) from posts').fetchone()
    conLink.close()

    global connCounter
    connCounter += 1
    metricsObject['db_connection_count'] = connCounter
    metricsObject['post_count'] = articleCounter[0]


def initialize_logger():
    log_level = os.getenv("LOGLEVEL", "DEBUG").upper()
    log_level = (
        getattr(logging, log_level)
        if log_level in ["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING",]
        else logging.DEBUG
    )

    logging.basicConfig(
        format='%(levelname)s:%(name)s:%(asctime)s, %(message)s',
                level=log_level,
    )

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
    # Logs:A non-existing article is accessed and a 404 page is returned.
      logging.error('Non existing Article with id{}='.format(post_id))  
      return render_template('404.html'), 404
    else:
    # Logs:An existing article is retrieved. The title of the article should be recorded in the log line.
      logging.info('An existing article with title {} is retrieved'.format(post['title']))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    # Logs:The "About Us" page is retrieved.
    logging.info('The "About Us" page is retrieved.')
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
            # Logs:A new article is created. The title of the new article should be recorded in the logline.
            logging.info('A new article is created with title= {}'.format(title))
            return redirect(url_for('index'))

    return render_template('create.html')

# Healthcheck endpoint
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


# Metrics endpoint
"""/metrics endpoint that would return the following:
An HTTP 200 status code
A JSON response with the following metrics:
Total amount of posts in the database
Total amount of connections to the database. For example, accessing an article will query the database, hence will count as a connection.
Example output: {"db_connection_count": 1, "post_count": 7}

Tips: The /metrics endpoint response should NOT be hardcoded."""
@app.route('/metrics', methods=['GET'])
def metrics():
    # define my dictionary metricsObject with the requirements
    metricsObject = {
                        'db_connection_count' : 0,
                        'post_count' : None
                    }

    # call to my custome fn and the first initial output: {"db_connection_count": 1, "post_count": 6}
    get_article_count(metricsObject)

    response = app.response_class(
                                     status = 200,
                                     response = json.dumps(metricsObject),
                                     mimetype = 'application/json'
                                 )

    return response



# start the application on port 3111
if __name__ == "__main__":
   """Logs:Every log line should include the timestamp and be outputted to the STDOUT and STDERR.
   Also, capture any Python logs at the DEBUG level.""" 
   # Logs configurations after using import logging
#    logging.basicConfig(level=logging.DEBUG) 
   initialize_logger()
   app.run(host='0.0.0.0', port='3111')
