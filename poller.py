import datetime
from typing import Optional
import argparse
from urllib.parse import quote
from dotenv import load_dotenv
import os
import json

from scrapfly import ScrapeConfig, ScrapflyClient, ScrapeApiResponse


def scrape_user(username: str, session: ScrapflyClient):
    file_path = 'data/' + username + ".json"
    if os.path.exists(file_path):
        print("already downloaded", username)
        with open(file_path, "r") as file:
            return json.load(file)
    else:
        """scrape user's data"""
        print("downloading", username)
        result = session.scrape(
            ScrapeConfig(
                url=f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
                headers={"x-ig-app-id": "936619743392459"},
                asp=True,
            )
        )
        data = json.loads(result.content)
        with open(file_path, "w") as file:
            json.dump(data["data"]["user"], file)

        """create directory for posts"""
        directory_path = "data/" + username

        # Create the directory if it doesn't exist
        if not os.path.exists(directory_path):
            os.mkdir(directory_path)
        return data["data"]["user"]


def scrape_user_posts(user_id: str, session: ScrapflyClient, cursor, page_size=12):
    """scrape user's post data"""
    print("starting from", cursor)
    base_url = "https://www.instagram.com/graphql/query/?query_hash=e769aa130647d2354c40ea6a439bfc08&variables="
    variables = {
        "id": user_id,
        "first": page_size,
        "after": cursor,
    }

    result = session.scrape(ScrapeConfig(base_url + quote(json.dumps(variables)), asp=True))
    posts = json.loads(result.content)["data"]["user"]["edge_owner_to_timeline_media"]
    for post in posts["edges"]:
        post_data = post["node"]
        timestamp = post_data["taken_at_timestamp"]
        dt = datetime.datetime.fromtimestamp(timestamp)

        id = post_data["id"]
        # print(id, post_data['edge_media_to_caption'], dt.isoformat())
        filename = 'data/' + username + "/" + dt.isoformat() + "-" + id + ".json"
        with open(filename, "w") as file:
            json.dump(post_data, file)

    page_info = posts["page_info"]
    if not page_info["has_next_page"]:
        return None
    else:
        return page_info["end_cursor"]


if __name__ == "__main__":

    # Create an argument parser
    parser = argparse.ArgumentParser()

    # Add the username option
    parser.add_argument("-u", "--username", help="The username")

    # Add the cursor option
    parser.add_argument("-c", "--cursor", help="The cursor")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the values of username and cursor
    username = args.username
    cursor = args.cursor

    # Load environment variables from .env file
    load_dotenv()

    # Access the value of the secret key
    scraplify_key = os.getenv("SCRAPLIFY_KEY")

    with ScrapflyClient(key=scraplify_key, max_concurrency=2) as session:

        result_user = scrape_user(username, session)
        cursor = scrape_user_posts(result_user["id"], session, cursor)
        while cursor:
            cursor = scrape_user_posts(result_user["id"], session, cursor)
            print("received", cursor)
