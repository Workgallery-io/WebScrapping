from bs4 import BeautifulSoup
import requests
from flask import *
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# remove unnecessary find_all and find methods and use try-except block to handle the error

@app.route("/", methods=["GET"])  # creating an endpoint for GET request
def home_page():
    return "<html><body style='margin: 1rem; padding: 1rem; font-family: monospace; font-size: 1.2rem; height: 100vh; background-color: #cdf4df; display: flex; flex-direction: column; justify-content: center; text-align: center; align-items: center'><h1 style='color: green'>Hello, Welcome to LEETCODE SCRAPPER's HOMEPAGE</h1> <h2>To get someone's LeetCode Account Details send GET request to the below URL  <p style='color: blue'>https://subrata-rudra-leetcode-scrapper.onrender.com/user/?user=LEETCODE_USERNAME_OF_USER</p></h2></body></html>"

@app.route("/user/", methods=["GET"])
def request_data():
    try:
        username = str(request.args.get("user"))
        print(username)
        base_url = "https://leetcode.com/"

        final_url = base_url + username

        html_text = requests.get(final_url).text

        soup = BeautifulSoup(html_text, "lxml")

        username = get_value(soup, "div", "text-label-3 dark:text-dark-label-3 text-xs")

        candidate_name = get_value(
            soup,
            "div",
            "text-label-1 dark:text-dark-label-1 break-all text-base font-semibold",
        )

        candidate_rank = get_value(
            soup, "span", "ttext-label-1 dark:text-dark-label-1 font-medium"
        )

        contest_attended = get_value(
            soup,
            "div",
            "text-label-1 dark:text-dark-label-1 font-medium leading-[22px]",
            index=1,
        )

        contest_rating = get_value(
            soup,
            "div",
            "text-label-1 dark:text-dark-label-1 flex items-center text-2xl",
        )

        contest_global_ranking = get_value(
            soup,
            "div",
            "text-label-1 dark:text-dark-label-1 font-medium leading-[22px]",
        )

        total_problem_solved = get_value(
            soup,
            "div",
            "text-[24px] font-medium text-label-1 dark:text-dark-label-1",
        )

        problems_solved = soup.find_all(
            "span",
            class_="mr-[5px] text-base font-medium leading-[20px] text-label-1 dark:text-dark-label-1",
        )

        language_used = soup.find_all(
            "span",
            class_="inline-flex items-center px-2 whitespace-nowrap text-xs leading-6 rounded-full text-label-3 dark:text-dark-label-3 bg-fill-3 dark:bg-dark-fill-3 notranslate",
        )

        solved_problem = soup.find_all(
            "span", class_="text-label-1 dark:text-dark-label-1 font-medium line-clamp-1"
        )

        topics_covered = soup.find_all(
            "span",
            class_="inline-flex items-center px-2 whitespace-nowrap text-xs leading-6 rounded-full bg-fill-3 dark:bg-dark-fill-3 cursor-pointer transition-all hover:bg-fill-2 dark:hover:bg-dark-fill-2 text-label-2 dark:text-dark-label-2",
        )

        badges_earned = soup.find_all(
            "img", class_="h-full w-full cursor-pointer object-contain"
        )

        most_recent_badge = get_value(
            soup, "div", "text-label-1 dark:text-dark-label-1 text-base"
        )

        language_used_list = [language.text for language in language_used]

        solved_problem_list = [problem.text for problem in solved_problem]

        topics_covered_list = [topic.text for topic in topics_covered]

        badges_earned_list = [badge["alt"] for badge in badges_earned]

        solved_problem_json = json.dumps(solved_problem_list)
        topics_covered_json = json.dumps(topics_covered_list)
        badges_earned_json = json.dumps(badges_earned_list)
        language_used_json = json.dumps(language_used_list)

        data_set = {
            "LeetCodeUsername": username,
            "CandidateName": candidate_name,
            "CandidateRank": candidate_rank,
            "ContestAttended": contest_attended,
            "ContestRating": contest_rating,
            "ContestGlobalRanking": contest_global_ranking,
            "TotalProblemsSolved": total_problem_solved,
            "EasyProblem": get_list_value(problems_solved, 0),
            "MediumProblem": get_list_value(problems_solved, 1),
            "HardProblem": get_list_value(problems_solved, 2),
            "MostRecentlyEarnedBadge": most_recent_badge,
            "Last15SolvedProblems": solved_problem_json,
            "TopicsCovered": topics_covered_json,
            "BadgesEarned": badges_earned_json,
            "LanguageUsed": language_used_json,
        }

        json_dump = json.dumps(data_set)
        return json_dump

    except Exception as e:
        error_message = f"Error: {str(e)}"
        return json.dumps({"error": error_message})


def get_value(soup, tag, class_name, index=0):
    try:
        return soup.find(tag, class_=class_name).text
    except (AttributeError, IndexError):
        return None


def get_list_value(lst, index):
    try:
        return lst[index].text
    except (IndexError, AttributeError):
        return None


if __name__ == "__main__":
    app.run()
