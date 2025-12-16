import subprocess
import time
import pyautogui
import pytesseract
import csv
import os
import re
from datetime import datetime, timedelta
import requests
import pyperclip
import json
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import keyboard
import sys
import ast

# Small delay before starting (useful if launched manually)
time.sleep(2)

# ================================
# CONFIGURATION (Windows)
# ================================

# Path to Chrome executable
CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

# Game URL
GAME_URL = "https://totalbattle.com/en/"

# Tesseract OCR executable path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Chest limits
MAX_CHESTS = 400

# Screen coordinates (hardcoded for current resolution/layout)
CLICK_CLAN_TAB = (1012, 950)
CLICK_CHESTS_TAB = (575, 461)

# OCR regions
CHEST_INFO_REGION = (788, 389, 432, 90)     # Chest name, From, Source
CHEST_TIME_REGION = (1310, 416, 93, 27)     # Remaining time

# Click to open chest
CLICK_OPEN_CHEST = (1347, 475)

# Stores the last valid chest generation timestamp
LAST_VALID_CHEST_DATE = None

# Accounts to process
ACCOUNTS = [
    {
        "email": "youraccount1@mail.com",
        "password": "12345678",
        "url": "https://yourdomain.com/chesttracker/reception_DATA_1.php"
    },
    {
        "email": "youraccount2@mail.com",
        "password": "12345678",
        "url": "https://yourdomain.com/chesttracker/reception_DATA_2.php"
    }
]

# ================================
# BROWSER / UI AUTOMATION
# ================================

def open_chrome(account_email, account_password):
    """Launch Chrome, log into Total Battle and navigate to Clan > Chests."""

    print("Opening Chrome with Total Battle...")

    subprocess.Popen([
        CHROME_PATH,
        "--incognito",
        "--start-maximized",
        "--no-first-run",
        "--disable-restore-session-state",
        GAME_URL
    ])

    # Wait for the page to load
    time.sleep(10)

    # Maximize window (double safety)
    pyautogui.hotkey('win', 'up')
    time.sleep(1)
    pyautogui.hotkey('win', 'up')
    time.sleep(1)

    # Accept cookies
    print("Accepting cookies...")
    pyautogui.click(1363, 978)
    time.sleep(2)

    # Login process
    print("Logging in...")
    pyautogui.click(427, 477)  # LOGIN button
    time.sleep(3)

    # Email field
    pyautogui.click(298, 455)
    pyperclip.copy(account_email)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)

    # Password field
    pyautogui.click(285, 518)
    pyautogui.typewrite(account_password)
    time.sleep(1)

    # Submit login
    pyautogui.click(392, 618)

    # Wait for the game to fully load
    time.sleep(90)

    # Close any popup/intro screen
    print("Closing popup (ESC)...")
    pyautogui.press('esc')
    time.sleep(4)

    # Navigate to Clan > Chests
    pyautogui.click(*CLICK_CLAN_TAB)
    time.sleep(1)
    pyautogui.click(*CLICK_CLAN_TAB)
    time.sleep(2)
    pyautogui.click(*CLICK_CHESTS_TAB)
    time.sleep(1)
    pyautogui.click(*CLICK_CHESTS_TAB)
    time.sleep(2)


def close_chrome():
    """Close Chrome by clicking the window close button."""
    print("Closing Chrome window...")
    pyautogui.click(1898, 19)

# ================================
# OCR & DATA PARSING
# ================================

def read_text(region, lang="eng"):
    """Take a screenshot of a region and extract text using OCR."""
    screenshot = pyautogui.screenshot(region=region)
    return pytesseract.image_to_string(screenshot, lang=lang).strip()


def calculate_chest_generation_time(text):
    """
    Given a remaining time string like '14h42m' or '1g9h36m',
    calculate the chest generation datetime (chests last 20h).
    """
    global LAST_VALID_CHEST_DATE

    if not text or not text.strip():
        text = "19h59m"

    # Normalize common OCR mistakes
    text = text.lower()
    text = text.replace("o", "0").replace("l", "1").replace("i", "1")
    text = text.replace("g", "9").replace("G", "9")

    clean_text = re.sub(r'[\s:]+', '', text)
    match = re.search(r'([0-9]{1,4})h([0-9]{1,4})m', clean_text)

    if not match:
        if LAST_VALID_CHEST_DATE:
            return LAST_VALID_CHEST_DATE
        hours_left, minutes_left = 19, 59
    else:
        try:
            hours_left = int(re.sub(r'\D', '', match.group(1))[:2])
            minutes_left = int(re.sub(r'\D', '', match.group(2))[:2])
        except ValueError:
            if LAST_VALID_CHEST_DATE:
                return LAST_VALID_CHEST_DATE
            hours_left, minutes_left = 19, 59

    hours_left = max(0, min(hours_left, 20))
    minutes_left = max(0, min(minutes_left, 59))

    elapsed = timedelta(hours=(20 - hours_left), minutes=-minutes_left)
    generated_at = datetime.now() - elapsed

    LAST_VALID_CHEST_DATE = generated_at.strftime("%Y-%m-%d %H:%M")
    return LAST_VALID_CHEST_DATE


def parse_chest_info(text):
    """
    Parse OCR text block and extract chest name, player and source.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        return {"chest": "", "player": "", "source": "", "valid": False}

    chest_name = lines[0]
    player = ""
    source = ""

    for line in lines[1:]:
        line = line.replace(";", ":")
        if line.lower().startswith("from"):
            player = line.split(":", 1)[1].strip()
        elif line.lower().startswith("source"):
            source = line.split(":", 1)[1].strip()

    return {
        "chest": chest_name,
        "player": player,
        "source": source,
        "valid": bool(player and source)
    }

# ================================
# CHEST PROCESSING
# ================================

def process_chest():
    raw_info = read_text(CHEST_INFO_REGION)
    chest_info = parse_chest_info(raw_info)

    if not chest_info.get("valid"):
        print("No valid 'From' or 'Source' detected. End of chest list.")
        return None

    raw_time = read_text(CHEST_TIME_REGION)
    generated_time = calculate_chest_generation_time(raw_time)

    # Open chest
    pyautogui.click(*CLICK_OPEN_CHEST)

    result = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "chest": chest_info["chest"],
        "player": chest_info["player"],
        "source": chest_info["source"],
        "generated": generated_time
    }

    print(result)
    return result

# ================================
# NETWORK / LOGGING
# ================================

def send_batch(data_list, url):
    """Send a batch of chest data to the server and log the response."""
    os.makedirs("logs_envios", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        response = requests.post(url, json=data_list, timeout=30)

        status = response.status_code
        text = response.text

        log_file = f"logs_envios/send_{timestamp}_{status}.txt"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(text)

    except Exception as e:
        log_file = f"logs_envios/send_{timestamp}_error.txt"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(str(e))
        return False

    return True

# ================================
# MAIN LOOP
# ================================

if __name__ == "__main__":
    print("Starting script (Ctrl+C to stop)")

    for account in ACCOUNTS:
        print("Processing account:", account["email"])

        open_chrome(account["email"], account["password"])

        try:
            time.sleep(5)
            chests = []
            for i in range(MAX_CHESTS):
                data = process_chest()
                if data is None:
                    break
                chests.append(data)

            if chests:
                send_batch(chests, account["url"])

        except Exception as e:
            print("Execution error:", e)

        close_chrome()
        time.sleep(5)

    print("All accounts processed. Script finished.")
