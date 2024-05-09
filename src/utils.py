import csv
import json
import os
from typing import List, Dict


def count_results(json_file: str) -> int:
    """
    Count the number of objects in the result field of a JSON file.
    """
    with open(json_file, "rb") as file:
        data = file.read()
        json_str = data.decode("utf-8")
        json_data = json.loads(json_str)
        return len(json_data.get("result", []))


def print_json_structure(data, indent=0):
    """Recursively prints the structure of a JSON object without values."""
    if isinstance(data, dict):
        for key in data:
            print('  ' * indent + key)
            print_json_structure(data[key], indent + 1)
    elif isinstance(data, list):
        if len(data) > 0:
            print('  ' * indent + 'List of:')
            print_json_structure(data[0], indent + 1)
        else:
            print('  ' * indent + 'Empty List')


def filter_submissions(submissions: List[Dict]) -> List[Dict]:
    """Filters submissions to keep only the first accepted per problem by author."""  # noqa
    contestant_submissions = [sub for sub in submissions if sub["author"]["participantType"] == "CONTESTANT"]  # noqa
    contestant_submissions.sort(key=lambda x: (x["author"]["members"][0]["handle"], x["creationTimeSeconds"], x["problem"]["index"]))  # noqa
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


def save_submissions_to_csv(submissions: List[Dict], filename: str):
    """Saves filtered submissions to a CSV file."""
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "id",
                "contest_id",
                "author_handle",
                "problem_index",
                "verdict",
                "relative_time_seconds",
                "creation_time_seconds",
            ]
        )
        for sub in submissions:
            writer.writerow([
                sub["id"],
                sub["contestId"],
                sub["author"]["members"][0]["handle"],
                sub["problem"]["index"],
                sub["verdict"],
                sub["relativeTimeSeconds"],
                sub["creationTimeSeconds"]
            ])


def create_slug(title: str) -> str:
    """Create a slug from a string by removing punctuation and converting to lowercase."""  # noqa
    import re
    # Remove all non-word characters (everything except numbers and letters)
    slug = re.sub(r"[^\w\s]", '', title)
    # Replace all runs of whitespace with a single dash
    slug = re.sub(r"\s+", '-', slug)
    # Convert to lowercase
    return slug.lower()


def save_contest_data(folder: str, contest_info: Dict):
    """Save contest information into a CSV file."""
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, "contest_info.csv")
    with open(filename, 'w', newline='') as file:
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
                "relative_time_seconds"
            ]
        )
        writer.writerow([
            contest_info["id"],
            contest_info["name"],
            contest_info["type"],
            contest_info["phase"],
            contest_info["frozen"],
            contest_info["durationSeconds"],
            contest_info["startTimeSeconds"],
            contest_info["relativeTimeSeconds"]
        ])


def save_problems_data(folder: str, problems: List[Dict]):
    """Save problem information into a CSV file."""
    filename = os.path.join(folder, "problems_info.csv")
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["index", "name", "type", "rating", "tags"])
        for problem in problems:
            tags = ','.join(problem["tags"])
            writer.writerow([
                problem["index"],
                problem["name"],
                problem["type"],
                problem["rating"],
                tags
            ])


# fieldnames = [
#     'submission_id',
#     'contest_id',
#     'creation_time_seconds',
#     'relative_time_seconds',
#     'problem_index',
#     'author_handle',
#     'participation_type',
#     'programming_language',
#     'verdict',
#     'test_set',
#     'passed_test_count',
#     'time_consumed_milliseconds',
#     'memory_consumed_bytes'
# ]

# row = {
#     'submission_id': sub['id'],
#     'contest_id': sub['contestId'],
#     'creation_time_seconds': sub['creationTimeSeconds'],
#     'relative_time_seconds': sub.get('relativeTimeSeconds', ''),
#     'problem_index': sub['problem']['index'],
#     'author_handle': sub['author']['members'][0]['handle'],
#     'participation_type': sub['author']['participantType'],
#     'programming_language': sub['programmingLanguage'],
#     'verdict': sub['verdict'],
#     'test_set': sub['testset'],
#     'passed_test_count': sub['passedTestCount'],
#     'time_consumed_milliseconds': sub['timeConsumedMillis'],
#     'memory_consumed_bytes': sub['memoryConsumedBytes']
# }


# print("Number of participants: ", count_results("participants.json"))
# print("Number of submissions: ", count_results("submissions.json"))
