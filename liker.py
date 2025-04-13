#!.venv\Scripts\python
import os
import platform
import sys

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager as CM

from selenium import webdriver
from utilities import (
    load_account_credentials,
    load_usernames,
    login,
    random_sleep,
    type_slowly,
)

if platform.system().lower().startswith("win"):
    from subprocess import CREATE_NO_WINDOW

ELEMENTS_TIMEOUT = 15
IG_BASE_URL = "https://www.instagram.com/"
IG_LOGIN_URL = "https://www.instagram.com/accounts/login/"


def liker():
    username, password = load_account_credentials()

    options = webdriver.ChromeOptions()

    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--lang=en")
    options.add_argument("--log-level=3")
    options.add_experimental_option("detach", True)

    dir_path = os.path.join(os.getcwd(), "selenium")
    options.add_argument(f"--user-data-dir={dir_path}")

    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_ELEMENTS_TIMEOUT_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/535.19"
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    browser = webdriver.Chrome(service=ChromeService(CM().install()), options=options)

    if platform.system().lower().startswith("win"):
        browser.service.creation_flags = CREATE_NO_WINDOW

    browser.set_window_size(600, 1000)

    browser.get(IG_LOGIN_URL)

    random_sleep()

    if browser.current_url != IG_BASE_URL:
        login(browser, username, password)

    like_most_recent_posts(browser)


def like_most_recent_posts(browser):
    usernames, usernames_contacted, usernames_failed = load_usernames()

    like_quantity = int(input("How many accounts would you like to interact with?: "))
    while len(usernames_contacted) < like_quantity:
        if not usernames:
            print("Out of usernames. Exiting early.")
            break

        username = usernames.pop()

        try:
            explore_button = WebDriverWait(browser, ELEMENTS_TIMEOUT).until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        '//a[@href="/explore/"]',
                    )
                )
            )
            explore_button.click()
        except:
            print("Error: Can't find Explore button.")
            browser.close()
            browser.quit()
            sys.exit()

        random_sleep()

        try:
            to_field = WebDriverWait(browser, ELEMENTS_TIMEOUT).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "(//input[contains(@placeholder,'Search')])[2]")
                )
            )
            type_slowly(to_field, username)
        except:
            print("Error: To field not found. Unable to look up username.")
            handle_failure_to_like(username, usernames)
            break

        random_sleep()


#! TODO: Implement Post Liking Functionality
def handle_post_liked(username, usernames_contacted):
    print(f"Success: Message Sent to {username}")
    usernames_contacted.append(username)


#! TODO: Implement Post Liking Failure Functionality
def handle_failure_to_like(username, usernames):
    print(f"Error: Failed To Send Message to {username}.")
    usernames.append(username)


if __name__ == "__main__":
    liker()
