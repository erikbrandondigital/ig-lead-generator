#!.venv\Scripts\pythonw
import os
import sys
import time
import shutil
import json
import platform
import PySimpleGUI as sg
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager as CM

if platform.system().lower().startswith("win"):
    from subprocess import CREATE_NO_WINDOW

# FOR TESTING ==================
# username = ''
# password = ''
# ==============================

ELEMENTS_TIMEOUT = 15
FOLLOW_DATA_LOADING_TIMEOUT = 6

IG_BASE_URL = "https://www.instagram.com/"
IG_LOGIN_URL = "https://www.instagram.com/accounts/login/"
IG_ACCOUNT_URL = "https://www.instagram.com/{}/"
IG_FOLLOWERS_URL = "https://www.instagram.com/{}/followers/"
IG_FOLLOWINGS_URL = "https://www.instagram.com/{}/following/"


def initGUI():
    layout = [
        [
            sg.Text("Target Account:"),
            sg.InputText(key="target", enable_events=True),
        ],
        [
            sg.Text("Quantity:"),
            sg.InputText(key="quantity", enable_events=True, default_text="50"),
        ],
        [
            sg.Button(
                "Scrape Followers", key="followers", enable_events=True, disabled=True
            ),
            sg.Button(
                "Scrape Followings", key="followings", enable_events=True, disabled=True
            ),
            sg.Button("Reset Browser", key="reset", enable_events=True),
            sg.Button("Exit", key="exit"),
            sg.Text("", key="loading_text"),
        ],
    ]

    window = sg.Window("Instagram Scraper", layout, keep_on_top=True)

    while True:
        input_fields_complete = False
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "exit":
            window.close()
            sys.exit()

        if (
            event == "target"
            and values["target"]
            and values["target"][-1]
            not in ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._")
        ):
            window["target"].update(values["target"][:-1])

        if event == "target" and len(values["target"]) > 30:
            window["target"].update(values["target"][:-1])

        if (
            event == "quantity"
            and values["quantity"]
            and values["quantity"][-1] not in ("0123456789")
        ):
            window["quantity"].update(values["quantity"][:-1])

        if event == "quantity" and len(values["quantity"]) > 4:
            window["quantity"].update(values["quantity"][:-1])

        if event == "target" or event == "quantity":
            if len(values["target"]) and len(values["quantity"]) > 0:
                input_fields_complete = True

        if input_fields_complete:
            window.find_element("followers").Update(disabled=False)
            window.find_element("followings").Update(disabled=False)

        else:
            window.find_element("followers").Update(disabled=True)
            window.find_element("followings").Update(disabled=True)

        if event == "reset":
            clearSelenium()

        if event == "followers" or event == "followings":
            window["loading_text"](f"Scraping Target {event.capitalize()}...")
            window.Disable()

            window.perform_long_operation(
                lambda: init(
                    values["target"],
                    int(values["quantity"]),
                    event,
                ),
                "done",
            )

        if event == "done":
            window["loading_text"]("")
            window["target"]("")
            window["quantity"]("")
            window.Enable()


def init(target, quantity, mode):
    with open("data/config/account.json") as file:
        missing_credentials = False
        account = json.load(file)
        username = account[0]["username"]
        password = account[0]["password"]
        if not username:
            print("Error: Username not set in account config.")
            missing_credentials = True
        if not password:
            print("Error: Password not set in account config.")
            missing_credentials = True
        if missing_credentials:
            print(
                "Make sure the account credentials you entered are correct in > 'data/config/account.json'"
            )
        file.close()

    options = webdriver.ChromeOptions()
    # TODO: invoking in headless removes need for GUI

    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--lang=en")
    options.add_argument("--log-level=3")
    options.add_experimental_option("detach", True)

    dir_path = os.path.join(os.getcwd(), "selenium")
    options.add_argument(f"--user-data-dir={dir_path}")

    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/535.19"
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    chrome_service = ChromeService("chromedriver")

    if platform.system().lower().startswith("win"):
        chrome_service.creation_flags = CREATE_NO_WINDOW

    bot = webdriver.Chrome(
        executable_path=CM().install(), options=options, service=chrome_service
    )
    bot.set_window_size(600, 1000)

    bot.get(IG_LOGIN_URL)

    time.sleep(2)

    if bot.current_url == IG_BASE_URL:
        scrape(bot, target, quantity, mode)
    else:
        login(bot, username, password, target, quantity, mode)


def login(bot, username, password, target, quantity, mode):
    print("Logging in...")

    user_element = WebDriverWait(bot, ELEMENTS_TIMEOUT).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input')
        )
    )

    user_element.send_keys(username)

    time.sleep(1)

    pass_element = WebDriverWait(bot, ELEMENTS_TIMEOUT).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input')
        )
    )

    pass_element.send_keys(password)

    time.sleep(1)

    login_button = WebDriverWait(bot, ELEMENTS_TIMEOUT).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="loginForm"]/div/div[3]/button')
        )
    )

    login_button.click()

    time.sleep(10)

    scrape(bot, target, quantity, mode)


def scrape(bot, target, quantity, mode):
    # target = input("Enter Your Target Username: ")

    bot.get(IG_ACCOUNT_URL.format(target))

    time.sleep(5)

    # stats = bot.find_elements_by_class_name("_ac2a")
    # num_followers = float((stats[1].text).replace(',', '.'))

    # print('Followers: ' + str(num_followers))

    # quantity = int(
    #     input(
    #         "Enter How many followers you want to scrape (make sure the value is integer): "
    #     )
    # )

    # getting followers
    if quantity > 0:
        if mode == "followers":
            bot.get(IG_FOLLOWERS_URL.format(target))
        else:
            bot.get(IG_FOLLOWINGS_URL.format(target))

        time.sleep(3.5)

        ActionChains(bot).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(
            Keys.SHIFT
        ).perform()
        ActionChains(bot).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(
            Keys.SHIFT
        ).perform()

    print("Scraping...")

    accounts = set()

    not_loading_count = 0
    prev = 0
    while len(accounts) < quantity:
        ActionChains(bot).send_keys(Keys.END).perform()

        time.sleep(5)

        more_accounts = bot.find_elements(By.XPATH, '//*/div[@role="button"]/a')

        accounts.update(more_accounts)

        # print(len(followers))
        if len(accounts) == prev:
            not_loading_count += 1
        else:
            not_loading_count = 0
        if not_loading_count == FOLLOW_DATA_LOADING_TIMEOUT:
            break
        prev = len(accounts)

    user_accounts = list()
    c = 0
    for i in accounts:
        if i.get_attribute("href"):
            c += 1
            account = i.get_attribute("href").split("/")[3]
            print(i.get_attribute("href"))
            user_accounts.append(account)
            # print (c, ' ', follower)
        else:
            continue

    user_accounts = user_accounts[:quantity]

    print("Saving to file...")
    print(
        "[DONE] - Your scraped accounts have been saved in the data > scraper folder."
    )

    export_file_name = f"data/{target}-{mode}-usernames.txt"

    with open(export_file_name, "w") as file:
        for user in user_accounts:
            file.write(user + "\n")
        file.close()

    print("Cleaning Up...")
    bot.quit()
    print("Waiting for orders...")


def clearSelenium():
    dir_path = os.path.join(os.getcwd(), "selenium")
    shutil.rmtree(dir_path, ignore_errors=True)


if __name__ == "__main__":
    initGUI()
