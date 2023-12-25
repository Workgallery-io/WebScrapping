from time import sleep

import requests
from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)


def scrape_data(profiles_input):
    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    exe_path = ChromeDriverManager().install()
    service = Service(exe_path)
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.linkedin.com/login")
    sleep(6)

    linkedin_username = "snehithb295@gmail.com"
    linkedin_password = "du-F+EY?D9t^c$2"

    driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[1]/input").send_keys(linkedin_username)
    driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[2]/input").send_keys(linkedin_password)
    sleep(3)
    driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[3]/button").click()

    profiles = profiles_input
    data = []
    for i in profiles:
        driver.get(i)
        sleep(5)
        title = driver.find_element(By.XPATH,
                                    "//h1[@class='text-heading-xlarge inline t-24 v-align-middle break-words']").text
        print(title)
        description = driver.find_element(By.XPATH,
                                          "//div[@class='text-body-medium break-words']").text
        print(description)
        data.append({"title": title, "description": description})
        sleep(4)
    driver.close()
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


@app.route('/scrape_github_profiles', methods=['POST'])
def scrape_github_profiles(username):
    url = f"https://api.github.com/users/{username}/repos"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        repositories = response.json()
        repo_list = []

        for repo in repositories:
            repo_info = {
                "name": repo["name"],
                "description": repo["description"],
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "url": repo["html_url"]
            }
            repo_list.append(repo_info)

        return repo_list
    else:
        return None


if __name__ == '__main__':
    app.run(debug=True)
