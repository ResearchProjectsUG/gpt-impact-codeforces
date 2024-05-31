import csv
import os
import re
from typing import List, Dict
from enums import ProblemTag


def print_json_structure(data, indent=0):
    """Recursively prints the structure of a JSON object without values."""
    if isinstance(data, dict):
        for key in data:
            print("  " * indent + key)
            print_json_structure(data[key], indent + 1)
    elif isinstance(data, list):
        if len(data) > 0:
            print("  " * indent + "List of:")
            print_json_structure(data[0], indent + 1)
        else:
            print("  " * indent + "Empty List")


def create_slug(title: str) -> str:
    """Create a slug from a string by removing punctuation and converting to lowercase."""  # noqa
    # Remove all non-word characters (everything except numbers and letters)
    slug = re.sub(r"[^\w\s]", "", title)
    # Replace all runs of whitespace with a single dash
    slug = re.sub(r"\s+", "-", slug)
    # Convert to lowercase
    return slug.lower()


def filter_submissions(submissions: List[Dict]) -> List[Dict]:
    """Filters submissions to keep only until the first accepted per problem by contestants."""  # noqa
    contestant_submissions = [
        sub for sub in submissions if sub["author"]["participantType"] == "CONTESTANT"  # noqa
    ]
    contestant_submissions.sort(
        key=lambda x: (
            x["author"]["members"][0]["handle"],
            x["creationTimeSeconds"],
            x["problem"]["index"],
        )
    )
    filtered_submissions = []
    seen_authors_and_problems = set()

    for submission in contestant_submissions:
        author_handle = submission["author"]["members"][0]["handle"]
        problem_index = submission["problem"]["index"]
        author_problem_key = (author_handle, problem_index)

        if author_problem_key not in seen_authors_and_problems:
            filtered_submissions.append(submission)
            if submission["verdict"] == "OK":
                seen_authors_and_problems.add(author_problem_key)

    return filtered_submissions


def save_contest_data(folder: str, contest_info: Dict):
    """Save contest information into a CSV file."""
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, "contest.csv")
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "id",
                "name",
                "type",
                "phase",
                "frozen",
                "duration_seconds",
                "start_time_seconds",
                "relative_time_seconds",
            ]
        )
        writer.writerow(
            [
                contest_info["id"],
                contest_info["name"],
                contest_info["type"],
                contest_info["phase"],
                contest_info["frozen"],
                contest_info["durationSeconds"],
                contest_info["startTimeSeconds"],
                contest_info["relativeTimeSeconds"],
            ]
        )


def save_problems_data(folder: str, problems: List[Dict]):
    """Save problem information into a CSV file."""
    filename = os.path.join(folder, "problems.csv")
    headers = ["index", "name", "type", "rating"] + [
        tag.value for tag in ProblemTag
    ]

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for problem in problems:
            # Initialize the row with problem details
            row = [
                problem["index"],
                problem["name"],
                problem["type"],
                problem["rating"],
            ]

            # Initialize tag columns to 0
            tag_data = {tag.value: 0 for tag in ProblemTag}

            # Set to 1 the tags present in the problem
            for tag in problem["tags"]:
                tag_data[tag] = 1

            # Append the tag data maintaining the order of headers
            row.extend(tag_data[tag.value] for tag in ProblemTag)
            writer.writerow(row)


def save_submissions_data(folder: str, submissions: List[Dict]):
    """Saves filtered submissions to a CSV file with reordered columns."""
    filename = os.path.join(folder, "submissions.csv")
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "contest_id",
            "problem_index",
            "id",
            "programming_language",
            "verdict",
            "relative_time_seconds",
            "creation_time_seconds",
            "author_handle",
            "participation_type",
            "test_set",
            "passed_test_count",
            "time_consumed_milliseconds",
            "memory_consumed_bytes",
        ])
        for sub in submissions:
            writer.writerow([
                sub["contestId"],
                sub["problem"]["index"],
                sub["id"],
                sub["programmingLanguage"],
                sub["verdict"],
                sub["relativeTimeSeconds"],
                sub["creationTimeSeconds"],
                sub["author"]["members"][0]["handle"],
                sub["author"]["participantType"],
                sub["testset"],
                sub["passedTestCount"],
                sub["timeConsumedMillis"],
                sub["memoryConsumedBytes"],
            ])


def save_user_data(folder: str, users: List[Dict]):
    """Save user data into a CSV file."""
    filename = os.path.join(folder, "users.csv")
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "handle",
                "first_name",
                "last_name",
                "country",
                "city",
                "rating",
                "max_rating",
                "rank",
                "max_rank",
                "organization",
            ]
        )
        for user in users:
            writer.writerow(
                [
                    user["handle"],
                    user.get("firstName", ""),
                    user.get("lastName", ""),
                    user.get("country", ""),
                    user.get("city", ""),
                    user["rating"],
                    user["maxRating"],
                    user["rank"],
                    user["maxRank"],
                    user.get("organization", ""),
                ]
            )
