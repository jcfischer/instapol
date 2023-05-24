from flask import Flask, render_template, request, redirect, url_for
import requests
import os
import sqlite3

DATABASE = '../data_new/zoe.db'

app = Flask(__name__)


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
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Retrieve the filter parameters from the request
    filters = request.args.copy()
    filters.pop('page', None)

    # Pagination parameters
    page = int(request.args.get('page', 1))
    per_page = 10
    print("page", page)
    # Construct the SQL query with the filters
    query = "SELECT id, username, display_url, caption, ocr_caption, comment_count, timestamp FROM posts ORDER by timestamp"
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
    conn = sqlite3.connect(DATABASE)
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


@app.route('/post/<post_id>', methods=['POST'])
def edit_post_details(post_id):
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    referendum = request.form.get('referendum', '')
    direct_camp = request.form.get('direct_camp', '')
    strategy = request.form.get('strategy', '')
    info_struct = request.form.get('info_struct', '')
    info_posit = request.form.get('info_posit', '')
    neg_strat = request.form.get('neg_strat', '')
    neg_focus = request.form.get('neg_focus', '')
    neg_inciv = request.form.get('neg_inciv', '')
    twostep_strat = request.form.get('twostep_strat', '')
    neg_target = request.form.get('neg_target', '')

    # Execute a query to update the "dat" column with the formatted value
    cursor.execute("""
        UPDATE posts
        SET dat = strftime('%d%m%y', timestamp)
        WHERE id = ?
    """, (post_id,))
    # Retrieve the post details for the given post_id

    cursor.execute("""
            UPDATE posts
            SET referendum = :referendum,
            direct_camp = :direct_camp,
            strategy = :strategy,
            info_struct = :info_struct, 
            info_posit = :info_posit,
            neg_strat = :neg_strat,
            neg_focus = :neg_focus,
            neg_inciv = :neg_inciv,
            twostep_strat = :twostep_strat,
            neg_targ =  :neg_target
            WHERE id = :key
        """, {'referendum': referendum,
              'direct_camp': direct_camp,
              'strategy': strategy,
              'info_struct': info_struct,
              'info_posit': info_posit,
              'neg_strat': neg_strat,
              'neg_focus': neg_focus,
              'neg_inciv': neg_inciv,
              'twostep_strat': twostep_strat,
              'neg_target': neg_target,
              'key': post_id})

    cursor.execute("""
        SELECT *
        FROM posts
        WHERE referendum IS NULL
        ORDER BY timestamp
        LIMIT 1
    """)
    result = cursor.fetchone()
    next_id = result[0]
    print("next entry:", next_id)

    # Close the database connection
    cursor.close()
    conn.commit()
    conn.close()

    # redirect to the next post that is not processed yet
    return redirect(url_for('show_post_details', post_id=next_id))


def construct_where_clause(filters):
    conditions = []
    for column, value in filters.items():
        if not value == '':
            conditions.append(f"{column} = '{value}'")
    return " AND ".join(conditions)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
