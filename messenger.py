#!.venv\Scripts\pythonw
import json
import random
import sys
from pathlib import Path
from src.instadm import InstaDM

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

if len(sys.argv) > 1:
    with open(sys.argv[1]) as file:
        usernames = file.read().splitlines()
        usernames_contacted = []
        file.close()
else:
    print(
        "\nERROR | No Text File Found: Please Drag & Drop A Text File Onto This Script To try Again.\n"
    )
    sys.exit()

with open("data/config/messages.txt", "r") as file:
    messages = [line.strip() for line in file]
    file.close()


dm_num = int(input("How many DMs do you want to send?: "))

# Auto login
insta = InstaDM(username, password, headless=False)

for i in range(dm_num):
    if not usernames:
        print("Out of usernames. Exiting early.")
        break

    username = usernames.pop()
    # Send message
    # insta.sendMessage(
    #     user=username,
    #     message=random.choice(messages).replace("@USERNAME", username),
    # )
    usernames_contacted.append(username)
    print(random.choice(messages).replace("@USERNAME", username))

insta.teardown()

print(f"Done. {len(usernames_contacted)} DMs Sent.")

file_name_parts = Path(sys.argv[1]).name.split("-", 3)[:2]
export_file_name = f"data/{'-'.join(file_name_parts)}-usernames-messaged.txt"

with open(export_file_name, "a") as file:
    for user in usernames_contacted:
        file.write(user + "\n")
    file.close()

with open(sys.argv[1], "w") as file:
    for user in usernames:
        file.write(user + "\n")
    file.close()
