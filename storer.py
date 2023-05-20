import argparse
import sqlite3
import json
import datetime
import os

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Load Instagram JSON data into SQLite database')
# Add the username option
parser.add_argument("-u", "--username", help="The username")

args = parser.parse_args()

# Connect to SQLite database
conn = sqlite3.connect('data/instagram.db')
cursor = conn.cursor()

# Create table
cursor.execute('''CREATE TABLE IF NOT EXISTS posts
                  (id TEXT PRIMARY KEY,
                   username TEXT,
                   display_url TEXT,
                   caption TEXT,
                   ocr_caption TEXT,
                   comment_count INTEGER,
                   timestamp DATETIME)''')

# Iterate over JSON files in the directory
username = args.username

directory = 'data/' + username
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        file_path = os.path.join(directory, filename)

        # Load JSON data from the file
        with open(file_path, 'r') as file:
            json_data = json.load(file)

        # Extract relevant information
        post_id = json_data['id']
        display_url = json_data['display_url']
        caption = json_data['edge_media_to_caption']['edges'][0]['node']['text']
        comment_count = json_data['edge_media_to_comment']['count']
        timestamp = json_data['taken_at_timestamp']

        # Convert Unix timestamp to a formatted datetime string
        datetime_string = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


        # Insert data into the table
        cursor.execute("INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (post_id, username, display_url, caption, "", comment_count, datetime_string))

# Commit changes and close the connection
conn.commit()
conn.close()
