import json
import os
import shutil
import sys
from random import randint, uniform
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def random_sleep(minimum=2, maximum=7):
    duration = randint(minimum, maximum)
    sleep(duration)


def type_slowly(element, input_text=""):
    for character in input_text:
        element.send_keys(character)
        sleep(uniform(0.005, 0.02))


def reset_browser():
    dir_path = os.path.join(os.getcwd(), "selenium")
    shutil.rmtree(dir_path, ignore_errors=True)


def load_account_credentials():
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
            sys.exit(
                "Make sure the account credentials you entered are correct in > 'data/config/account.json'"
            )
        file.close()

    return username, password


def load_account_credentials_gui(window):
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
            window.close()
            sys.exit(
                "Make sure the account credentials you entered are correct in > 'data/config/account.json'"
            )
        file.close()

    return username, password


def load_messages():
    with open("data/config/messages.txt", "r") as file:
        messages = [line.strip() for line in file]
        file.close()
        return messages


def load_usernames():
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as file:
            usernames = file.read().splitlines()
            usernames_contacted = []
            usernames_failed = []
            file.close()
            return (usernames, usernames_contacted, usernames_failed)
    else:
        print(
            "\nError | No Text File Found: Please Drag & Drop A Text File Onto This Script To try Again.\n"
        )
        sys.exit()


def login(browser, username, password):
    print("Logging in...")

    ELEMENTS_TIMEOUT = 15

    try:
        user_element = WebDriverWait(browser, ELEMENTS_TIMEOUT).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input')
            )
        )
        type_slowly(user_element, username)
    except:
        raise NoSuchElementException("Unable to find login field or type in username.")

    random_sleep()

    try:
        pass_element = WebDriverWait(browser, ELEMENTS_TIMEOUT).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input')
            )
        )
        type_slowly(pass_element, password)
    except:
        raise NoSuchElementException(
            "Unable to find password field or type in password."
        )

    random_sleep()

    try:
        login_button = WebDriverWait(browser, ELEMENTS_TIMEOUT).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="loginForm"]/div/div[3]/button')
            )
        )
        login_button.click()
    except:
        raise NoSuchElementException("Unable to find login button or click it.")

    random_sleep()
