# tb-chesttracker
---
## Project Overview

This repository contains a set of Python scripts designed to automate the extraction of chest data from the game **Total Battle** using UI automation and OCR.

The project is composed of **two main scripts**, each with a clearly defined purpose.

---

## 1. Screen Region Selector (Helper Tool)

This utility script is used to **capture screen coordinates and regions** required by the main automation bot.

It displays a fullscreen, semi-transparent overlay that allows the user to **drag the mouse to select a screen area**.
Once a region is selected, the script prints and displays the exact coordinates `(x, y, width, height)`.

### Purpose

* Obtain accurate screen coordinates for:

  * Click positions
  * OCR capture regions
* These coordinates are later **copied and replaced directly in the main automation script**
* Helps adapt the bot to different screen resolutions or UI layouts

This script does **not perform any automation by itself**.
It is a **support tool** used during setup and calibration.

---

## 2. Main Automation Script (Chest Reader Bot)

The main script automates the process of collecting chest information from the game.

### High-level workflow

1. Launches **Google Chrome** in incognito mode
2. Opens the Total Battle website
3. Performs the **login process**
4. Navigates to:

   * Clan section
   * Chest / Gifts section
5. Iterates through the available chests **one by one**
6. For each chest:

   * Opens it
   * Reads the chest information using **OCR (Tesseract)**
   * Extracts:

     * Chest name
     * Player name (`From`)
     * Source (crypt, event, etc.)
     * Estimated chest generation time
7. Accumulates the extracted data
8. Sends the data in batches to a **PHP backend endpoint** via HTTP POST
9. Logs server responses for traceability and debugging

### Key features

* Fully UI-driven automation using `pyautogui`
* OCR-based text extraction using `pytesseract`
* Robust handling of OCR errors and corrupted text
* Batch-based data submission to reduce network calls
* Designed to process **multiple accounts sequentially**
* Logging of successful and failed submissions

---

## Notes & Limitations

* All screen coordinates are **resolution and UI dependent**
* The script assumes:

  * Windows OS
  * Google Chrome installed in the default path
  * Tesseract OCR installed and properly configured
* UI changes in the game may require recalibrating coordinates using the helper script

---

## Disclaimer

This project is intended for **educational and personal use only**.
It relies on UI automation and screen scraping, which may be affected by game updates or platform changes.
