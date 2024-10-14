import json
from typing import Any
import pandas as pd

def main():
        with open("data/raw/contest_list.json", encoding = "utf-8") as f:
                raw_contests: list[dict[str, Any]] = json.load(f)["result"]
        
        raw_contests = [contest for contest in raw_contests if contest["phase"] == "FINISHED"]
        contests_df: pd.DataFrame = pd.DataFrame(raw_contests)
        contests_df.to_csv("data/processed/contests.csv", index = False)

if __name__ == "__main__":
        main()
