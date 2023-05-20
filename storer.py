import argparse
import sqlite3
import json
import datetime
import os
import pytesseract
from PIL import Image
import requests
from io import BytesIO

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Load Instagram JSON data into SQLite database')
# Add the username option
parser.add_argument("-u", "--username", help="The username(s) - separate multiple by comma")
parser.add_argument("-d", "--database", help="The filename of the database")

args = parser.parse_args()
username = args.username
db = args.database

# Connect to SQLite database
conn = sqlite3.connect('data/' + db)
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



names_list = username.split(',')


def ocr_image(image_url):
    print("Downloading", image_url)
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    text = pytesseract.image_to_string(image, lang='deu')
    print(text)
    return text

for name in names_list:
    print(name)

    directory = 'data/' + name

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            try:
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

                # Check if the record already exists
                cursor.execute("SELECT id FROM posts WHERE id=:post_id", {'post_id': post_id})
                existing_record = cursor.fetchone()

                if existing_record is None:
                    ocr_text = ocr_image(display_url)
                    # Insert data into the table using named parameters
                    cursor.execute(
                        "INSERT INTO posts VALUES (:post_id, :username, :display_url, :caption, :ocr_text, :comment_count, :timestamp)",
                        {'post_id': post_id, 'username': name, 'display_url': display_url, 'caption': caption,
                         'ocr_text': ocr_text, 'comment_count': comment_count, 'timestamp': datetime_string})
            except (ValueError, KeyError, IndexError):
                print(f"Error processing JSON file: {file_path}")

            conn.commit()
# Commit changes and close the connection
conn.commit()
conn.close()
