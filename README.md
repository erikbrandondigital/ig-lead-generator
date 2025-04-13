# IG-Lead-Generator

This python lead generator can scrape a chosen quantity of followers or followings of any target account and send direct messages to IG users. Currently, it runs on Windows & Mac OS.

# Installation

## 1. Clone The Repo

Clone the repo to a folder on your local computer using HTTPS, SSH or Zip download from GitHub.

## 2. Set Up A Virtual Environment

On Windows:

- Run `python -m venv .venv` in your terminal while in the project directory.
- Activate the environment by running `.\venv\Scripts\activate`.

On MacOS:

- Run `virtualenv .venv` in your terminal while in the project directory.
- Activate the environment by running `source .venv/bin/activate`.

## 3. Install Required Python Modules

On Windows:

- Run `python -m pip install -r requirements.txt`.

On MacOS:

- Run `pip3 install -r requirements.txt`.

## 4. Configure Account & Messages

In the data > config folder:

- Add your IG account credentials to the `account-example.json` file and rename the file to `account.json`.
- Modify the IG message to your liking in `messages-example.txt` and rename the file to `messages.txt`.

## 5. Run the Scraper

- Double-click `scraper.pyw` and enter the target account and quantity. Then click `Scrape Followers` or `Scrape Followings`.
- After the scraper finishes, a list of followers or followings will appear in the data folder in a text file.

## 6. Run the Messenger.

- Drag & drop a text file containing a list of usernames from the scraper onto the messenger.py script.
- Enter the number of accounts you want to DM.
- Wait for the bot to DM the total number of accounts.
- After all messages are sent, the lead generator will generate separate text files of accounts that were successfully messaged and unsuccessfully messaged. Accounts that were not messaged because the message limit was reached first will remain in the original text file of accounts that was dragged onto the messenger.py script.

## 7. Run the Liker.

- Coming Soon...

# Common Issues & Solutions

- Fix for PySimpleGUI Tkinter attribute error on MacOs 13 & greater.
  https://github.com/fsmosca/Python-Easy-Chess-GUI/issues/41#issuecomment-878709295

# Additional Notes

This is a private fork built upon the codebase of the repo located here: https://github.com/pythontester192/Instagram-Bot-Scrape-DM-Users
