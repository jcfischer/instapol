# instapol
Instagram Scraper for political data


## Prerequisites:

- Scraplify API key and subscription  https://scrapfly.io/dashboard
- Python 3.11 (`brew install python3`)
- Required libraries: (`pip3 install -r requirements.txt`)
- Tesseract OCR engine (`brew install Tesseract`)
- SQLite Browser: https://sqlitebrowser.org/dl/
- 
- 
## Usage

1. Download the raw JSON files for an instagram account:

   `$ python3 ./poller -u spschweiz`

   If you need to restart and don't want to download everything again, you can specify the last
   cursor position that the script returned

   `$ python3 ./poller -u spschweiz -c xxxyyyy`

   and the download will start from that page

   This creates a JSON file for the account information (`spschweiz.json`) in the `data` directory and
   downloads all messages into a directory called `spschweiz`. The JSON files
   are named `TIMESTAMP-ID.json` where TIMESTAMP is the ISO-8601 date that the post 
   was created and `id` is the Instagram ID

## References

Basic original code to scrape Instagram taken from: https://scrapfly.io/blog/how-to-scrape-instagram/