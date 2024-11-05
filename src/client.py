import logging
import os
import requests
import time
import utils
from config import settings
from enums import Language
from typing import Dict, Any


class CodeforcesClient:
    def __init__(self):
        self.base_url = settings.CODEFORCES_BASE_URL
        self.last_request_time = None
        self.request_interval = 2  # Min interval between requests in seconds
        self.max_retries = 3  # Max number of retries for a failed request

    def build_url(self, resource: str) -> str:
        """Construct the full API endpoint URL."""
        return f"{self.base_url}/{resource}"

    def wait_for_next_request(self):
        """Ensure the requests are spaced out by at least `request_interval` seconds."""  # noqa
        if self.last_request_time is not None:
            elapsed_time = time.time() - self.last_request_time
            if elapsed_time < self.request_interval:
                time.sleep(self.request_interval - elapsed_time)
        self.last_request_time = time.time()

    def fetch_data(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """Generic method to fetch data from a given Codeforces API endpoint."""  # noqa
        url = self.build_url(endpoint)
        self.wait_for_next_request()
        attempt = 0
        while attempt < self.max_retries:
            try:
                logging.info(f"Requesting URL {url} with params {params}")
                response = requests.get(url, params=params)
                response.raise_for_status()  # Raises an HTTP error for bad responses  # noqa
                logging.info("Request successful.")
                return response.json()  # Assuming the API returns JSON data
            except requests.RequestException as e:
                logging.error(f"Request failed: {e}")
                attempt += 1
                time.sleep(2)
                if attempt == self.max_retries:
                    logging.error("Maximum retry attempts reached, moving to next request")  # noqa
        return None


def process_contest_data(client: CodeforcesClient, contest_id: int):
    """Process and save all relevant contest data."""

    # Fetch contest standings
    contest_standings_params = {
        "contestId": contest_id,
        "asManager": False,
        "from": 1,
        "count": 5,
        "showUnofficial": False,
    }

    json_data = client.fetch_data(
        "contest.standings",
        contest_standings_params,
    )

    if json_data is None:
        return

    contest_info = json_data["result"]["contest"]
    problems = json_data["result"]["problems"]

    # Fetch user rated list
    user_rated_list_params = {
        "activeOnly": False,
        "includeRetired": True,
        "contestId": contest_id,
    }

    json_data = client.fetch_data("user.ratedList", user_rated_list_params)

    if json_data is None:
        return

    users = json_data["result"]

    # Fetch contest submissions
    contest_submissions_params = {
        "contestId": contest_id,
        "asManager": False,
        "from": 1,
        "count": 10000000,
        "lang": Language.ENGLISH,
    }

    json_data = client.fetch_data("contest.status", contest_submissions_params)

    if json_data is None:
        return

    submissions = json_data["result"]
    filtered_submissions = utils.filter_submissions(submissions)

    contest_rating_changes_params = {
        "contestId": contest_id,
        "lang": Language.ENGLISH,
    }
    json_data = client.fetch_data("contest.ratingChanges", contest_rating_changes_params)  # noqa

    if json_data is None:
        return

    rating_changes = json_data["result"]

    # Save data to CSV
    slug = utils.create_slug(contest_info["name"])
    slug_folder = os.path.join(settings.BASE_DATA_PATH, slug)
    os.makedirs(slug_folder, exist_ok=True)  # Ensure the directory exists

    utils.save_contest_data(slug_folder, contest_info)
    utils.save_problems_data(slug_folder, problems)
    utils.save_user_data(slug_folder, users)
    utils.save_submissions_data(slug_folder, filtered_submissions)
    utils.save_rating_changes_data(slug_folder, rating_changes)

    print(f"Data has been saved in folder {slug_folder}")


def process_relevant_contests(client: CodeforcesClient):
    """Fetches contests, filters, and processes relevant contests."""
    response = client.fetch_data("contest.list", {"gym": False})
    contests = response["result"]
    relevant_keywords = ["Round", "Hello", "Good Bye"]

    for contest in contests:
        if any(keyword in contest["name"] for keyword in relevant_keywords) and contest["phase"] == "FINISHED" and contest["id"] != 1014 and contest["id"] != 925 and not os.path.exists(os.path.join(settings.BASE_DATA_PATH, utils.create_slug(contest["name"]))):  # noqa
            print("Processing data for", contest["name"], end = ": ")
            process_contest_data(client, contest["id"])


client = CodeforcesClient()
process_relevant_contests(client)
