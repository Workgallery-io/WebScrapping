import requests
import base64
from flask import Flask, jsonify, request
from linkedin_api import Linkedin

app = Flask(__name__)

linkedin = Linkedin("snehithb295@gmail.com", "du-F+EY?D9t^c$2")


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
