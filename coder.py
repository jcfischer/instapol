import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect('data/zoe_code.db')
cursor = connection.cursor()

# List of words to check
words_to_check = ['freiheit', 'referendum', 'missbrauch', 'töten', 'tod', 'tot']

# Iterate through each word
for word in words_to_check:
    # Check the 'caption' field
    cursor.execute("UPDATE posts SET care_code = 1 WHERE caption LIKE ? COLLATE NOCASE", ('%{}%'.format(word),))
    # Check the 'ocr_caption' field
    cursor.execute("UPDATE posts SET care_code = 1 WHERE ocr_caption LIKE ? COLLATE NOCASE", ('%{}%'.format(word),))

# Set 'care_code' to 0 for the records where the words didn't occur
cursor.execute("UPDATE posts SET care_code = 0 WHERE care_code IS NULL")

# Commit the changes and close the connection
connection.commit()
connection.close()