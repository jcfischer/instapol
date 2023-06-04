import argparse
import sqlite3
import json
import datetime
import os
import pytesseract
from PIL import Image
import requests
from io import BytesIO

DATA_PATH = 'data_new/'

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Load Instagram JSON data into SQLite database')
# Add the username option
parser.add_argument("-u", "--username", help="The username(s) - separate multiple by comma")
parser.add_argument("-d", "--database", help="The filename of the database")

args = parser.parse_args()
username = args.username
db = args.database

# Connect to SQLite database
conn = sqlite3.connect(DATA_PATH + db)
cursor = conn.cursor()

# Create table

cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
                "id"	TEXT,
                "username"	TEXT,
                "display_url"	TEXT,
                "caption"	TEXT,
                "ocr_caption"	TEXT,
                "comment_count"	INTEGER,
                "timestamp"	DATETIME,
                "coder"	INTEGER DEFAULT 1,
                "Dat"	TEXT,
                "referendum"	INTEGER,
                "polparty"	INTEGER,
                "direct_camp"	INTEGER,
                "strategy"	INTEGER,
                "info_struct"	INTEGER,
                "info_posit"	INTEGER,
                "moral_care"	INTEGER,
                "moral_fair"	INTEGER,
                "moral_loyal"	INTEGER,
                "moral_auth"	INTEGER,
                "moral_sanct"	INTEGER,
                "moral_libert"	INTEGER,
                "neg_strat"	INTEGER,
                "neg_targ"	INTEGER,
                "neg_focus"	INTEGER,
                "neg_inciv"	INTEGER,
                "twostep_strat"	INTEGER,
                PRIMARY KEY("id"))''')

# Iterate over JSON files in the directory


names_list = username.split(',')

parties = {'svpch': 1,
           'spschweiz': 2,
           'fdp_schweiz': 3,
           'mitte_centre': 4,
           'gruenech': 5,
           'grunliberale': 6}


def ocr_image(image_url, id):
    print("Downloading", image_url)
    text = ''
    image_path = f"server/static/images/{id}.jpg"  # Assuming the images folder exists

    response = requests.get(image_url)
    if response.status_code == 200:
        # Save the image to a local directory
        with open(image_path, 'wb') as image_file:
            image_file.write(response.content)

        image = Image.open(BytesIO(response.content))
        text = pytesseract.image_to_string(image, lang='deu')
        print(text)
    else:
        print("could not get image:", id)
    return text


for name in names_list:
    print(name)

    directory = DATA_PATH + name

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

                pol_party = parties[name]

                # Convert Unix timestamp to a formatted datetime string
                datetime_string = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                dat = datetime.datetime.fromtimestamp(timestamp).strftime('%d%m%Y')

                # Check if the record already exists
                cursor.execute("SELECT id FROM posts WHERE id=:post_id", {'post_id': post_id})
                existing_record = cursor.fetchone()

                if existing_record is None:
                    ocr_text = ocr_image(display_url, post_id)
                    # Insert data into the table using named parameters
                    cursor.execute(
                        '''INSERT INTO posts (id, username, display_url, caption, ocr_caption, 
                          comment_count, timestamp, dat, polparty) 
                          VALUES (:post_id, :username, :display_url, :caption, :ocr_caption, 
                          :comment_count, :timestamp, :dat, :polparty)''',
                        {'post_id': post_id, 'username': name, 'display_url': display_url, 'caption': caption,
                         'ocr_caption': ocr_text, 'comment_count': comment_count, 'timestamp': datetime_string,
                         'dat': dat, 'polparty': pol_party})
                else:
                    print(post_id)
            except Exception as e:
                print(f"Error processing JSON file: {file_path}")
                print(str(e))

            conn.commit()
# Commit changes and close the connection
conn.commit()
conn.close()
