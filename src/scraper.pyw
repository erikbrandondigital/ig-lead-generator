import os
import platform
import sys

import FreeSimpleGUI as sg
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager as CM

from selenium import webdriver
from utilities import load_account_credentials_gui, login, random_sleep, reset_browser

if platform.system().lower().startswith("win"):
    from subprocess import CREATE_NO_WINDOW

FOLLOW_DATA_LOADING_TIMEOUT = 6

IG_BASE_URL = "https://www.instagram.com/"
IG_LOGIN_URL = "https://www.instagram.com/accounts/login/"
IG_ACCOUNT_URL = "https://www.instagram.com/{}/"


def initGUI():

    layout = [
        [
            sg.Text("Target Account:"),
            sg.Input(key="target", enable_events=True),
        ],
        [
            sg.Text("Quantity:"),
            sg.Input(key="quantity", enable_events=True, default_text="50"),
        ],
        [
            sg.Button(
                "Scrape Followers", key="followers", enable_events=True, disabled=True
            ),
            sg.Button(
                "Scrape Following", key="following", enable_events=True, disabled=True
            ),
            sg.Button("Reset Browser", key="reset", enable_events=True),
            sg.Button("Exit", key="exit"),
            sg.Text("", key="loading_text"),
        ],
    ]

    window = sg.Window("Instagram Scraper", layout, keep_on_top=True)

    username, password = load_account_credentials_gui(window)

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
            window.find_element("following").Update(disabled=False)

        else:
            window.find_element("followers").Update(disabled=True)
            window.find_element("following").Update(disabled=True)

        if event == "reset":
            reset_browser()

        if event == "followers" or event == "following":
            window["loading_text"](f"Scraping Target {event.capitalize()}...")
            # window.disable()

            window.perform_long_operation(
                lambda: init(
                    values["target"], int(values["quantity"]), event, username, password
                ),
                "done",
            )

        if event == "done":
            window["loading_text"]("")
            window["target"]("")
            window["quantity"]("")
            # window.enable()


def init(target, quantity, mode, username, password):
    options = webdriver.ChromeOptions()

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

    browser = webdriver.Chrome(service=ChromeService(CM().install()), options=options)

    if platform.system().lower().startswith("win"):
        browser.service.creation_flags = CREATE_NO_WINDOW

    browser.set_window_size(600, 1000)

    browser.get(IG_LOGIN_URL)

    random_sleep()

    if browser.current_url != IG_BASE_URL:
        login(browser, username, password)

    scrape(browser, target, quantity, mode)


def scrape(browser, target, quantity, mode):
    ELEMENTS_TIMEOUT = 15

    browser.get(IG_ACCOUNT_URL.format(target))

    random_sleep()

    if quantity > 0:
        if mode == "followers":
            try:
                followers_link_xpath = (
                    f'//a[@role="link" and @href="/{target}/followers/"]'
                )
                followers_link = WebDriverWait(browser, ELEMENTS_TIMEOUT).until(
                    EC.visibility_of_element_located((By.XPATH, followers_link_xpath))
                )
                followers_link.click()
            except:
                raise NoSuchElementException("Unable to click followers list link.")
        else:
            try:
                following_link_xpath = (
                    f'//a[@role="link" and @href="/{target}/following/"]'
                )
                following_link = WebDriverWait(browser, ELEMENTS_TIMEOUT).until(
                    EC.visibility_of_element_located((By.XPATH, following_link_xpath))
                )
                following_link.click()
            except:
                raise NoSuchElementException("Unable to click following list link.")

        random_sleep()

        ActionChains(browser).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(
            Keys.SHIFT
        ).perform()
        ActionChains(browser).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(
            Keys.SHIFT
        ).perform()

    print("Scraping...")

    accounts = set()

    not_loading_count = 0
    prev = 0
    while len(accounts) < quantity:
        ActionChains(browser).send_keys(Keys.END).perform()

        random_sleep()

        more_accounts = browser.find_elements(By.XPATH, '//*/div[@role="button"]/a')

        accounts.update(more_accounts)

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
            print(i.get_attribute("href"))
            account = i.get_attribute("href").split("/")[3]
            user_accounts.append(account)
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
    browser.close()
    browser.quit()
    print("Waiting for orders...")


if __name__ == "__main__":
    initGUI()
