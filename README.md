# Stock-Fidelity-Scraper

A custom python program for getting stock prices from Yahoo Finance via web scraping (BeautifulSoup) and for getting Fidelity investment account balances and monetary changes via web automation (Selenium & chromedriver)

This file was built with automation in mind, so it can be easily automated with Windows Task Scheduler.

Some packages you'll need to run this:
- The most up to date version of Selenium
- Undetected chromedriver with the .exe placed in the same location as your Python executable file (where Python is stored on your computer)

You'll also need:
- A text file with stock symbols line by line for beginning the stock price scraping
- Your Fidelity account login info in the variables of "username" and "password" in yahooFinance.py
- To add the names of the rows in the "column" list variable within fidelity.savedata()

This file is not to be used for monetary gain. All code within this file is subject to personal use ONLY.
