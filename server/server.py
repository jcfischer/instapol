from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from dotenv import load_dotenv
import os
import sqlite3
import csv
from forms.ConfigForm import CodingForm

app = Flask(__name__)
auth = HTTPBasicAuth()

# Load environment variables from .env file
load_dotenv()

# Access the value of the secret key
password = os.getenv("PASSWORD")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE = os.getenv('DATABASE')
users = {
    "zoe": generate_password_hash(password),
    "jcf": generate_password_hash(password)
}


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


# Route for displaying the list of posts
@app.route('/')
@auth.login_required
def show_posts():
    # Connect to the SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve the filter parameters from the request
    filters = request.args.copy()
    filters.pop('page', None)

    # Pagination parameters
    page = int(request.args.get('page', 1))
    per_page = 30
    print("page", page)
    # Construct the SQL query with the filters
    query = "SELECT id, username, caption, referendum, timestamp FROM posts ORDER by timestamp"
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
@auth.login_required
def show_post_details(post_id):
    # Connect to the SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve the post details for the given post_id
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    # Close the database connection

    form = CodingForm(obj=post)
    form.referendum.default = post['referendum']
    form.direct_camp.default = post['direct_camp']
    form.strategy.default = post['strategy']
    form.info_struct.default = post['info_struct']
    form.info_posit.default = post['info_posit']
    form.neg_strat.default = post['neg_strat']
    form.neg_focus.default = post['neg_focus']
    form.neg_inciv.default = post['neg_inciv']
    form.twostep_strat.default = post['twostep_strat']
    form.neg_targ.default = post['neg_targ']

    form.process()

    cursor.execute("SELECT count(*) FROM posts WHERE referendum IS NULL")
    remaining = cursor.fetchone()

    cursor.close()
    conn.close()
    print(remaining[0])
    # Render the template to display the post details
    return render_template('post_detail.html', post=post, form=form, remaining=remaining[0])


@app.route('/download_csv', methods=['GET'])
def download_csv():
    # Connect to the SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute a SELECT query to fetch data from the database
    cursor.execute("SELECT * FROM posts ORDER BY timestamp")

    # Fetch all rows from the query result
    rows = cursor.fetchall()

    # Define the CSV file path
    csv_file_path = 'data.csv'

    # Write the data to a CSV file
    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([i[0] for i in cursor.description])  # Write header row
        writer.writerows(rows)  # Write data rows

    # Close the database connection
    conn.close()

    # Send the CSV file as a downloadable response
    return send_file(csv_file_path, as_attachment=True)


@app.route('/post/<post_id>', methods=['POST'])
@auth.login_required
def edit_post_details(post_id):
    # Connect to the SQLite database
    conn = get_db_connection()
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
    neg_targ = request.form.get('neg_targ', '')

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
            neg_targ =  :neg_targ
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
              'neg_targ': neg_targ,
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
    app.run(port=8000, debug=False, host="0.0.0.0")
