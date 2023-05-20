from flask import Flask, render_template, request
from flask_cors import CORS
import requests
import os
import sqlite3

app = Flask(__name__)
CORS(app)


def cache_image(id, url):
    image_path = f"static/images/{id}.jpg"  # Assuming the images folder exists
    if os.path.exists(image_path):
        print(image_path)
    else:
        response = requests.get(url)
        if response.status_code == 200:
            # Save the image to a local directory
            with open(image_path, 'wb') as image_file:
                image_file.write(response.content)


# Route for displaying the list of posts
@app.route('/')
def show_posts():
    # Connect to the SQLite database
    conn = sqlite3.connect('../data/zoe.db')
    cursor = conn.cursor()

    # Retrieve the filter parameters from the request
    filters = request.args.copy()
    filters.pop('page', None)

    # Pagination parameters
    page = int(request.args.get('page', 1))
    per_page = 10
    print("page", page)
    # Construct the SQL query with the filters
    query = "SELECT id, username, display_url, caption, ocr_caption, comment_count, timestamp FROM posts"
    where_clause = construct_where_clause(filters)
    if where_clause:
        query += " WHERE " + where_clause

    # Count the total number of posts
    print(query)
    count_query = f"SELECT COUNT(*) FROM ({query}) AS count_query"
    cursor.execute(count_query)
    total_count = cursor.fetchone()[0]

    # Calculate the offset for pagination
    offset = (page - 1) * per_page

    # Add pagination to the SQL query
    query += f" LIMIT {per_page} OFFSET {offset}"

    # Execute the SQL query
    cursor.execute(query)
    posts = cursor.fetchall()

    # Close the database connection
    cursor.close()
    conn.close()

    # Calculate the total number of pages
    total_pages = (total_count + per_page - 1) // per_page

    # Render the template to display the filtered list of posts with pagination
    return render_template('post_list.html', posts=posts, total_pages=total_pages, current_page=page, request=request)


# Route for displaying the details of a specific post
@app.route('/post/<post_id>')
def show_post_details(post_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('../data/zoe.db')
    cursor = conn.cursor()

    # Retrieve the post details for the given post_id
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    image_url = post[2]
    print(image_url)
    cache_image(post_id, image_url)
    # Close the database connection
    cursor.close()
    conn.close()

    # Render the template to display the post details
    return render_template('post_detail.html', post=post)


def construct_where_clause(filters):
    conditions = []
    for column, value in filters.items():
        if not value == '':
            conditions.append(f"{column} = '{value}'")
    return " AND ".join(conditions)


if __name__ == '__main__':
    app.run()
