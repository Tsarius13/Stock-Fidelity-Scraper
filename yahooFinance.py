import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import date, datetime
from os.path import exists
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import time


class yahoo:

    def __init__(self):
        # Variables holding multiple components of the search url, BeautfifulSoup input, and various other components
        self.headers = {"Accept-Language": "en-US, en;q=0.5"}
        self.base_url = "https://finance.yahoo.com/quote/"
        self.url, self.price_text = "", ""
        self.lines, self.prices, self.symbols = [], [], []
        self.csvExists = False

    # This function reads a .csv or text file for stock symbols to scrape
    # and calls the necessary scrape function
    def fileRead(self):

        # Check if a stock price .csv already exists to read symbols, else read from provided text file
        if exists("StockPrices.csv"):
            self.csvExists = True

            # Check if prices have already been grabbed today
            data = pd.read_csv("StockPrices.csv")
            if ("Close " + str(date.today())) in data:
                exit(0)
            else:
                # Constructs the url needed for scraping the designated stock symbol
                # and calls scraping function
                for item in data["Symbol"]:
                    self.symbols.append(item)
                    self.url = self.base_url + item
                    self.url.rstrip(' ')
                    self.scrape()

        else:
            f = open('StockSymbols.txt', 'r')
            lines = f.readlines()
            for item in lines:
                symbol = str(item).strip()
                self.symbols.append(symbol)
                self.url = self.base_url + symbol
                self.url.rstrip(' ')
                self.scrape()

        # Calls the function for saving the retrieved data to .csv file
        self.saveCSV()

    # Scrapes stock prices and stores them using the appropriate class variables
    def scrape(self):
        results = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(results.text, "html.parser")

        stock_Price = soup.find_all('div', class_="D(ib) Mend(20px)")
        for price in stock_Price:
            price_text = price.text

        # In case the price cannot be retrieved, this is handled and an empty string is added for the symbol
        try:
            texts = re.split(r'[+-]', price_text)
            # In some cases, prices won't change and won't be caught by the regex,
            # this block catches that edge case
            if len(texts[0]) > 15:
                texts2 = texts[0].split(' ')
                self.prices.append(texts2[0])
            else:
                self.prices.append(texts[0])
        # In the case of an error, stores the error message in a text log with time and date
        # and continues program, adding an empty string for the symbol
        except UnboundLocalError as err:
            with open('Stock Price Error Log.txt', 'a') as file:
                file.write('\n' + str(err) + ' for ' +
                           self.url + ' @ ' + str(datetime.now()))
            self.prices.append("")

    # Saves the scraped prices to a new or existing .csv file using pandas dataframes
    # using today's date as the discerning header for the new column of data
    def saveCSV(self):
        if self.csvExists:
            # This block in particular creates a new dataframe for the scraped prices and merges it
            # with the created dataframe containg existing price data from the .csv
            df_csv = pd.read_csv("StockPrices.csv")
            df = pd.DataFrame({
                'Close': self.prices
            })
            df_csv['Close ' + str(date.today())
                   ] = df['Close']
            df_csv.to_csv("StockPrices.csv", index=False)
        else:
            dateString = 'Close ' + str(date.today())
            stocks = pd.DataFrame({
                'Symbol': self.symbols,
                dateString: self.prices
            })
            stocks.index += 1
            stocks.to_csv('StockPrices.csv')


class fidelity():

    # Initializes variables holding multiple components for Selenium, the Fidelity account, and the account data
    def __init__(self):
        self.balances, self.dollarChange, self.percentChange, self.all = [], [], [], []
        # Insert your username and password here
        self.username, self.password = '', ''

    # Gets account data via headless browser and account login. The saves data to multiple lists for dataframe creation
    def getData(self):

        # Sets up headless browser, navigates to Fidelity.com, and logs in using username and password
        opts = Options()
        opts.add_argument("--headless")
        driver = uc.Chrome(options=opts)
        driver.get(
            'https://digital.fidelity.com/prgw/digital/login/full-page?AuthRedUrl=digital.fidelity.com/ftgw/digital/portfolio/summary')
        time.sleep(5)
        searchForm = driver.find_element(By.ID, 'userId-input')
        searchForm.send_keys(self.username)
        time.sleep(5)
        searchForm = driver.find_element(By.ID, 'password')
        searchForm.send_keys(self.password)
        searchForm.submit()
        time.sleep(10)

        # Obtains balance, change in dollars, and change in percent of each investment account within the user account
        # In case data cannot be retrived, notes that in the error log on the appropriate date
        try:
            accounts = driver.find_elements(
                By.CLASS_NAME, "acct-selector__acct-balance")
            if not accounts:
                raise Exception
            for element in accounts:
                self.balances.append(element.text.replace('$', ''))

            monetaryChange = driver.find_elements(
                By.CLASS_NAME, "acct-selector__acct-gain-loss")
            if not monetaryChange:
                raise Exception

            # Popping the absolute total change (combined change of all accounts)
            monetaryChange.pop(0)
            for element in monetaryChange:
                change = element.text.split('(')
                self.dollarChange.append(change[0].replace('$', ''))
                newChange = change[1].replace('(', '')
                newChange = change[1].replace(')', '')
                self.percentChange.append(newChange)
        except Exception:
            with open('Fidelity Error Log.txt', 'a') as file:
                file.write('\n' + "Data was not able to be retrieved" +
                           ' @ ' + str(datetime.now()))
            driver.quit()
            exit(0)
        time.sleep(20)
        for i in range(len(self.balances)):
            self.all.append(self.balances[i])
            self.all.append(self.dollarChange[i])
            self.all.append(self.percentChange[i])

        # Calls method to save data to .csv
        self.saveData()

    # Checks if the .csv file exists, and if so, appends the data to it
    # Else will create the file and add the data
    def saveData(self):
        if exists('FidelityAccounts.csv'):
            data = pd.read_csv("FidelityAccounts.csv")
            if ("Close " + str(date.today())) in data:
                exit(0)
            else:
                df_csv = pd.read_csv("FidelityAccounts.csv")
                df = pd.DataFrame({
                    'Close': self.all
                })
                df_csv['Close ' + str(date.today())
                       ] = df['Close']
                df_csv.to_csv("FidelityAccounts.csv", index=False)
        else:
            dateString = 'Close ' + str(date.today())
            # Row names in the format of "Account name", "Dollar change", "Percent change"
            column = ["", "", "",
                      "", "", "",
                      "", "", ""]
            accounts = pd.DataFrame({
                'Identifiers': column,
                dateString: self.all
            })
            accounts.index += 1
            accounts.to_csv('FidelityAccounts.csv')


# Program entry point
if __name__ == "__main__":
    y = yahoo()
    y.fileRead()
    f = fidelity()
    f.getData()
