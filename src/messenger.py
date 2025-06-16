#!.venv\Scripts\python
import os
import platform
import sys
from pathlib import Path
from random import choice

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager as CM

from selenium import webdriver
from utilities import (
    load_account_credentials,
    load_messages,
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


def messenger():
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

    send_messages(browser)


def send_messages(browser):
    usernames, usernames_contacted, usernames_failed = load_usernames()
    messages = load_messages()

    try:
        messenger_button = WebDriverWait(browser, ELEMENTS_TIMEOUT).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//a[contains(@aria-label, 'Direct messaging')]",
                )
            )
        )
        messenger_button.click()
    except:
        print("Error: Can't find Direct Messaging button.")
        browser.close()
        browser.quit()
        sys.exit()

    random_sleep()

    dm_quantity = int(input("How many accounts do you want to message?: "))
    while len(usernames_contacted) < dm_quantity:
        if not usernames:
            print("Out of usernames. Exiting early.")
            break

        username = usernames.pop()

        try:
            new_message_button = WebDriverWait(browser, ELEMENTS_TIMEOUT).until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "(//*[name()='svg'][@aria-label='New message'])[1]",
                    )
                )
            )
            new_message_button.click()
        except:
            print("Error: New message button not found.")
            handle_failure_to_send(username, usernames)
            break

        random_sleep()

        try:
            to_field = WebDriverWait(browser, ELEMENTS_TIMEOUT).until(
                EC.visibility_of_element_located((By.NAME, "queryBox"))
            )
            type_slowly(to_field, username)
        except:
            print("Error: To field not found. Unable to look up username.")
            handle_failure_to_send(username, usernames)
            break

        random_sleep()

        try:
            account_xpath = (
                f'//div[@role="button" and .//span[contains(., "{username}")]]'
            )
            selected_account = WebDriverWait(browser, ELEMENTS_TIMEOUT).until(
                EC.visibility_of_element_located((By.XPATH, account_xpath))
            )
            selected_account.click()
        except:
            handle_cant_find_account(browser, username, usernames_failed)
            try:
                close_button = WebDriverWait(browser, ELEMENTS_TIMEOUT).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '(//*[name()="svg"][@aria-label="Close"])[1]')
                    )
                )
                close_button.click()
                continue
            except:
                print("Can't find close button. Unable to continue.")
                handle_failure_to_send(username, usernames)
                break

        random_sleep()

        try:
            next_button = WebDriverWait(browser, ELEMENTS_TIMEOUT).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//button/*[text()="Next"]')
                )
            )
            next_button.click()
        except:
            print("Error: Couldn't find next button. Can't proceed to send message.")
            handle_failure_to_send(username, usernames)
            break

        random_sleep()

        try:
            message_box = WebDriverWait(browser, ELEMENTS_TIMEOUT).until(
                EC.visibility_of_element_located((By.TAG_NAME, "textarea"))
            )
            type_slowly(message_box, choice(messages).replace("@USERNAME", username))
        except:
            print("Error: Can't find message box. Can't type message.")
            handle_failure_to_send(username, usernames)
            break

        random_sleep()

        try:
            send_button = WebDriverWait(browser, ELEMENTS_TIMEOUT).until(
                EC.visibility_of_element_located((By.XPATH, '//div[text()="Send"]'))
            )
            send_button.click()
        except:
            print("Error: Can't find send button. Can't send message.")
            handle_failure_to_send(username, usernames)
            break

        handle_message_sent(username, usernames_contacted)

        random_sleep()

    browser.close()
    browser.quit()

    export_contacted_usernames(usernames_contacted)
    export_failed_usernames(usernames_failed)
    export_remaining_usernames(usernames)

    print(
        f"{len(usernames_contacted)}/{dm_quantity} Sent. {len(usernames_failed)} Failed To Send."
    )


def handle_message_sent(username, usernames_contacted):
    print(f"Success: Message Sent to {username}")
    usernames_contacted.append(username)


def handle_failure_to_send(username, usernames):
    print(f"Error: Failed To Send Message to {username}.")
    usernames.append(username)


def handle_cant_find_account(browser, username, usernames_failed):
    print(f"Error: Couldn't find {username}'s account. Skipping.")
    usernames_failed.append(username)


def export_contacted_usernames(usernames_contacted):
    file_name_parts = Path(sys.argv[1]).name.split("-", 3)[:2]
    export_file_name = f"data/{'-'.join(file_name_parts)}-usernames-messaged.txt"

    with open(export_file_name, "a") as file:
        for user in usernames_contacted:
            file.write(user + "\n")
        file.close()


def export_failed_usernames(usernames_failed):
    file_name_parts = Path(sys.argv[1]).name.split("-", 3)[:2]
    export_file_name = f"data/{'-'.join(file_name_parts)}-usernames-failed.txt"

    with open(export_file_name, "a") as file:
        for user in usernames_failed:
            file.write(user + "\n")
        file.close()


def export_remaining_usernames(usernames):
    with open(sys.argv[1], "w") as file:
        for user in usernames:
            file.write(user + "\n")
        file.close()


if __name__ == "__main__":
    messenger()
