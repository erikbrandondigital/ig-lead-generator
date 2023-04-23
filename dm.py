#!.venv\Scripts\pythonw
import json
import random
import sys
import time
from pathlib import Path
from src.instadm import InstaDM

f = open(
    "data/config/accounts.json",
)
accounts = json.load(f)

if len(sys.argv) > 1:
    with open(sys.argv[1]) as f:
        usernames = f.read().splitlines()
        usernames_contacted = []
        f.close()
else:
    print(
        "\nERROR | No Text File Found: Please Drag & Drop A Text File Onto This Script To try Again.\n"
    )
    sys.exit()

with open("data/config/messages.txt", "r") as f:
    messages = [line.strip() for line in f]


dm_num = int(input("How many DMs do you want to send?: "))

for account in accounts:
    if not usernames:
        print("Out of usernames. Exiting early.")
        break
    # Auto login
    insta = InstaDM(
        username=account["username"], password=account["password"], headless=False
    )

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

with open(export_file_name, "w") as file:
    for user in usernames_contacted:
        file.write(user + "\n")
    file.close()

with open(sys.argv[1], "w") as file:
    for user in usernames:
        file.write(user + "\n")
    file.close()
