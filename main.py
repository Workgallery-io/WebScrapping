import requests
import base64
from flask import Flask, jsonify, request
from linkedin_api import Linkedin
from huggingface_hub import InferenceClient
from flask_cors import CORS

client = InferenceClient(
    "mistralai/Mistral-7B-Instruct-v0.1"
)
app = Flask(__name__)
CORS(app)

linkedin = Linkedin("snehithb295@gmail.com", "Test@476")


def scrape_data(profiles_input):
    profiles = profiles_input
    data = []
    for each_profile in profiles:
        profile = linkedin.get_profile(each_profile)
        data.append({
            "title": profile['summary'],
            "description": profile['headline'],
            "displayPictureUrl": profile['displayPictureUrl'],
            "experience": profile['experience'],
            "education": profile['education']
        })
    return data


@app.route('/scrape_linkedin_profiles', methods=['POST'])
def scrape_linkedin_profiles():
    try:
        request_data = request.json
        profiles_list = request_data.get('profiles', [])

        if not profiles_list:
            return jsonify({"error": "No profiles provided"}), 400

        # profiles_data = scrape_profiles(profiles_list)
        profiles_data = scrape_data(profiles_list)
        return jsonify({"profiles": profiles_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_readme_content(username, repo_name):
    url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        readme_data = response.json()
        if 'content' in readme_data:
            # Decode the content from Base64 encoding
            readme_content_base64 = readme_data['content']
            readme_content_bytes = base64.b64decode(readme_content_base64)
            readme_content = readme_content_bytes.decode('utf-8')
            return readme_content
        else:
            return ""  # Return empty string if README content is not present
    else:
        return ""  # Return empty string if README cannot be fetched


def split_paragraph(paragraph, max_length=1000):
    sentences = paragraph.split('. ')
    result_paragraphs = []

    current_paragraph = ""

    for sentence in sentences:
        if len(current_paragraph) + len(sentence) + 2 <= max_length:  # 2 for the space and period
            current_paragraph += sentence + '. '
        else:
            result_paragraphs.append(current_paragraph.strip())
            current_paragraph = sentence + '. '

    if current_paragraph:
        result_paragraphs.append(current_paragraph.strip())

    return result_paragraphs


@app.route('/summarize_text', methods=['POST'])
def summarize_text():
    request_data = request.json
    input_text = request_data.get('summarize_text', "No input received")
    paragraphs = split_paragraph(input_text)
    output = ""
    for paragraph in paragraphs:
        prompt = "[INST] summarize the text:" + paragraph + "   [/INST]"
        res = client.text_generation(prompt, max_new_tokens=95)
        output = output + res
    return output


@app.route('/scrape_github_profiles', methods=['POST'])
def scrape_github_profiles():
    request_data = request.json
    profiles_list = request_data.get('profiles', [])

    if not profiles_list:
        return jsonify({"error": "No profiles provided"}), 400

    for profile in profiles_list:
        url = f"https://api.github.com/users/{profile}/repos"
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        print(profile)
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            repositories = response.json()
            # print(repositories)
            repo_list = []

            for repo in repositories:
                print(repo)
                readme = get_readme_content(profile, repo["name"])
                repo_info = {
                    "name": repo["name"],
                    "description": repo["description"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "url": repo["html_url"],
                    "readme": readme
                }
                repo_list.append(repo_info)

            return repo_list
        else:
            return None

@app.route('/scrape_leetcode_profiles/user/',methods = ['GET'])
def scrape_leetcode_profile():
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

@app.route('/scrape_medium_profiles', methods=['POST'])
def scrape_medium_profiles():
    request_data = request.json
    profiles_list = request_data.get('profiles', [])

    if not profiles_list:
        return jsonify({"error": "No profiles provided"}), 400

    for profile in profiles_list:
        url = f"https://mediumpostsapi.vercel.app/api/{profile}"
        headers = {
            "Accept": "application/json"
        }
        print(profile)
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            posts = response.json()
            # print(repositories)
            repo_list = []

            for post in posts["dataMedium"]:
                print(post)
                repo_info = {
                    "title": post["title"],
                    "description": post["description"],
                }
                repo_list.append(repo_info)

            return repo_list
        else:
            return None


if __name__ == '__main__':
    app.run(debug=True)
