import argparse
import csv
import sqlite3

# Parse command line arguments
parser = argparse.ArgumentParser(description='Update SQLite database from CSV file')
parser.add_argument('-d', '--database', required=True, help='Path to the SQLite database file')
parser.add_argument('-c', '--csv', required=True, help='Path to the CSV file')
args = parser.parse_args()

# Connect to the SQLite database
conn = sqlite3.connect(args.database)
cursor = conn.cursor()

# Fetch the column names from the database
columns_query = "PRAGMA table_info(posts)"
cursor.execute(columns_query)
columns = [column[1] for column in cursor.fetchall()]

# Read the CSV file
with open(args.csv, 'r',  encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    data = [row for row in reader]

# Iterate over each row in the CSV data
for row in data:
    # Extract the values from the CSV row
    label = row['value.label']
    category = row['moral.foundation']
    word = row['word']

    # Split the category into type and virtue/vice
    category_parts = category.split('.')
    category_type = category_parts[0]
    category_subtype = category_parts[1]

    # Convert the word to lowercase
    lowercase_word = word.lower()

    # Query the SQLite database to find matching records
    query = f"SELECT * FROM posts WHERE (LOWER(caption) LIKE '%{lowercase_word}%' OR LOWER(ocr_caption) LIKE '%{lowercase_word}%')"
    cursor.execute(query)
    records = cursor.fetchall()


    num_records = len(records)
    print(f"Found {num_records} records matching the word '{word}'")

    for record in records:
        # Find the index of the label field in the columns list
        field_index = columns.index(label) if label in columns else -1

        if field_index != -1:
            existing_value = record[field_index]

            # Determine the new value based on the category subtype
            if category_subtype == 'virtue':
                new_value = 1
            elif category_subtype == 'vice':
                new_value = 2
            else:
                new_value = existing_value

            # Update the integer field based on the new value and existing value
            if existing_value != new_value:
                if existing_value in (None, 0):
                    record = record[:field_index] + (new_value,) + record[field_index + 1:]
                elif existing_value == 1 and new_value == 2:
                    record = record[:field_index] + (3,) + record[field_index + 1:]
                elif existing_value == 2 and new_value == 1:
                    record = record[:field_index] + (3,) + record[field_index + 1:]

            # Update the records in the database
            update_query = f"UPDATE posts SET {label} = ? WHERE id = ?"
            cursor.execute(update_query, (record[field_index], record[0]))



# Commit the changes to the database and close the connection
conn.commit()
conn.close()