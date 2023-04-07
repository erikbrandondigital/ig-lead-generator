#!.venv\Scripts\pythonw
import os
import sys
import time
import selenium
import PySimpleGUI as sg
from requests import get
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager as CM
from getpass import getpass


# FOR TESTING ==================
# username = ''
# password = ''
# ==============================

ELEMENTS_TIMEOUT = 15
FOLLOW_DATA_LOADING_TIMEOUT = 50

IG_BASE_URL = "https://www.instagram.com/"
IG_LOGIN_URL = "https://www.instagram.com/accounts/login/"
IG_ACCOUNT_URL = "https://www.instagram.com/{}/"
IG_FOLLOWINGS_URL = "https://www.instagram.com/{}/following/"


def initGUI():
    layout = [
        [sg.Text("Username:"), sg.InputText(key="username", enable_events=True)],
        [sg.Text("Password:"), sg.InputText(key="password", password_char="*")],
        [
            sg.Text("Target Account:"),
            sg.InputText(key="target", enable_events=True),
        ],
        [
            sg.Text("Quantity:"),
            sg.InputText(key="quantity", enable_events=True, default_text="50"),
        ],
        [
            sg.Button("Scrape", key="submit", enable_events=True, disabled=True),
            sg.Button("Exit", key="exit"),
            sg.Text("", key="loading_text"),
        ],
    ]

    window = sg.Window("Scrape Followings", layout)

    while True:
        input_fields_complete = False
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "exit":
            window.close()
            sys.exit()

        if (
            event == "username"
            and values["username"]
            and values["username"][-1]
            not in ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._")
        ):
            window["username"].update(values["username"][:-1])

        if event == "username" and len(values["username"]) > 30:
            window["username"].update(values["username"][:-1])

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

        if (
            event == "username"
            or event == "password"
            or event == "target"
            or event == "quantity"
        ):
            if (
                len(values["username"])
                and len(values["password"])
                and len(values["target"])
                and len(values["quantity"]) > 0
            ):
                input_fields_complete = True

        if input_fields_complete:
            window.find_element("submit").Update(disabled=False)
        else:
            window.find_element("submit").Update(disabled=True)

        if event == "submit":
            window["loading_text"]("Scraping Target...")
            window.Disable()

            window.perform_long_operation(
                lambda: init(
                    values["username"],
                    values["password"],
                    values["target"],
                    int(values["quantity"]),
                ),
                "done",
            )

        if event == "done":
            window["loading_text"]("")
            window["target"]("")
            window["quantity"]("")
            window.Enable()


def init(username, password, target, quantity):
    # username = input("Enter Your Username: ")
    # password = getpass.getpass("Enter Your Password: ")

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

    bot = webdriver.Chrome(executable_path=CM().install(), options=options)
    bot.set_window_size(600, 1000)

    bot.get(IG_LOGIN_URL)

    time.sleep(2)

    if bot.current_url == IG_BASE_URL:
        scrape(bot, target, quantity)
    else:
        login(bot, username, password, target, quantity)


def login(bot, username, password, target, quantity):
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

    scrape(bot, target, quantity)


def scrape(bot, target, quantity):
    # target = input("Enter Your Target Username: ")

    bot.get(IG_ACCOUNT_URL.format(target))

    time.sleep(5)

    # stats = bot.find_elements_by_class_name("_ac2a")
    # num_followings = float((stats[1].text).replace(',', '.'))

    # print('followings: ' + str(num_followings))

    # quantity = int(
    #     input(
    #         "Enter How many followings you want to scrape (make sure the value is integer): "
    #     )
    # )

    # getting followings
    if quantity > 0:
        bot.get(IG_FOLLOWINGS_URL.format(target))

        time.sleep(3.5)

        ActionChains(bot).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(
            Keys.SHIFT
        ).perform()
        ActionChains(bot).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(
            Keys.SHIFT
        ).perform()

    print("Scraping followings...")

    followings = set()

    not_loading_count = 0
    prev = 0
    while len(followings) < quantity:
        ActionChains(bot).send_keys(Keys.END).perform()

        time.sleep(5)

        more_followings = bot.find_elements(By.XPATH, '//*/div[@role="button"]/a')

        followings.update(more_followings)

        # print(len(followings))
        if len(followings) == prev:
            not_loading_count += 1
        else:
            not_loading_count = 0
        if not_loading_count == FOLLOW_DATA_LOADING_TIMEOUT:
            break
        prev = len(followings)

    users_followings = set()
    c = 0
    for i in followings:
        if i.get_attribute("href"):
            c += 1
            follower = i.get_attribute("href").split("/")[3]
            print(i.get_attribute("href"))
            users_followings.add(follower)
            # print (c, ' ', follower)
        else:
            continue

    print("Saving to file...")
    print("[DONE] - Your followings are saved in usernames.txt file")

    timestamp = time.strftime("%m-%d-%Y-%H%M%S")
    export_file_name = f"infos/{target}-following-usernames-{timestamp}.txt"

    with open(export_file_name, "w") as file:
        file.write("\n".join(users_followings) + "\n")

    print("Exiting...")
    bot.quit()


if __name__ == "__main__":
    initGUI()
