# IG-Lead-Generator

IG-Lead-Generator is a combination of Python scripts that can scrape a chosen quantity of followers or followings of any target account and send direct messages to IG users.

## Disclaimer

Please be aware that using Instagram bots or any form of automated tools for engaging with Instagram is against Instagram's Terms of Service. Instagram prohibits activities such as automated liking, following, commenting, and direct messaging.

By using my project to interact with Instagram in an automated fashion, you acknowledge and agree that you are doing so at your own risk and that I am in no way responsible for any outcomes associated with and resulting from the use of this software, including account suspension, permanent banning, shadow banning or any other form of penalties applied against your account by Instagram.

To Instagram, this project was created primarily for informational and educational purposes with the intent of learning how to scrape, crawl and interact with websites using Selenium. Any interactions between this project and Instagram users was limited to an amount that a single user is capable of producing by interacting with the Instagram platform directly.

# Prerequisites

To properly install and run this project you will need the following programming languages, software and tools:

1. [pyenv](https://github.com/pyenv/pyenv) >= 2.6.2
2. [Python](https://www.python.org) >= v3.12.3

# Installation

To install the project, follow the steps below:

## 1. Clone The Repo

Clone the repo to a folder on your machine from GitHub.

```
git clone https://github.com/erikbrandondigital/ig-lead-generator.git
```

## 2. Open The Project Folder

Open the project in your terminal or preferred file browser.

```
cd ig-lead-generator
```

## 3. Set Up & Activate a Python Virtual Environment

In your terminal run the following commands to install Python and create and activate a virtual environment.

```
pyenv install 3.12.3
pyenv virtualenv 3.12.3 ig-lead-generator-3.12.3
pyenv activate ig-lead-generator-3.12.3
```

## 3. Install Required Python Modules

With your pyenv virtual environment activated you can now install the Python packages, listed in the requirements.txt file, needed to run the application.

```
pip install -r requirements.txt
```

# Usage

To use the project, follow the steps below:

## 1. Configure Account & Messages

In the data > config folder:

- Copy & Rename the `account-example.json` file to `account.json` & Add your IG account credentials.
- Copy & Rename the `messages-example.txt` file to `messages.txt` & Modify the IG message to your liking.

**Note:** Only the `@USERNAME` placeholder can be used to insert usernames into the message.

## 2. Run the Scraper

To run the Scraper either double-click the `scraper.pyw` file in the `src` folder or execute the following command:

```
python src/scraper.pyw
```

1. Once it opens, enter the target account and quantity you would like to scrape.
2. Then click `Scrape Followers` or `Scrape Followings`.
3. After the scraper finishes, a list of followers or followings will appear in the `data` folder in a text file.

## 3. Run the Messenger.

To run the Messenger either drag & drop a text file containing a list of usernames onto the `messenger.py` script or include it as an argument in your terminal as shown in the following command:

```
python src/messenger.py data/instagram-followers-usernames.txt
```

1. Once it opens, enter the number of accounts you want to DM.
2. Wait for the bot to DM the total number of accounts.
3. After all messages are sent, the lead generator will generate separate text files of accounts that were successfully messaged and unsuccessfully messaged. Accounts that were not messaged because the message limit was reached first will remain in the original text file of accounts that was dragged onto the messenger.py script.

## 4. Run the Liker.

- Coming Soon...

# Common Issues & Solutions

- Fix for PySimpleGUI Tkinter attribute error on MacOs 13 & greater.
  https://github.com/fsmosca/Python-Easy-Chess-GUI/issues/41#issuecomment-878709295
