import requests
import os
import pickle
import pandas as pd
from bs4 import BeautifulSoup

class CompanyHolder():

    def __init__(self, PATH_TO_COMPANY_FILES, RELOAD = False):
        self.Symbols = None
        self.FullNames = None
        self.CSVNames = None
        self.sectors = None
        self.companies = None
        self.PATH_TO_COMPANY_FILES = PATH_TO_COMPANY_FILES
        if RELOAD:
            self.save_company_names(True)  
            
        self._load_companies()


    def _load_companies(self):

        """
        This function loads all available company symbols, company names and company csvnames.
        """
        if os.path.exists(self.PATH_TO_COMPANY_FILES + '/Companies.csv'):
            df = pd.read_csv(self.PATH_TO_COMPANY_FILES + '/Companies.csv')
            self.Symbols = list(df['Symbol'])
            self.FullNames = list(df['FullName'])
            self.CSVNames = list(df['CSVName'])
            self.sectors = list(df['Sector'])
            self.companies = df
        
        return

    def save_company_names(self,reload = False):
        """
        This function should only be called if we want to reload the companies. It overwrites the old company files and saves the present S&P500
        Companies.

        ATTENTION: NEW COMPANIES COULD CHANGE OVER TIME!
        """
        #this is a security measure such that the companies can not be reloaded by fault.
        if not reload:
            return

        # Get the html of the Wikipedia site to extract the table
        website_url = requests.get("https://en.wikipedia.org/w/index.php?title=List_of_S%26P_500_companies&oldid=895655255").text
        html_site = BeautifulSoup(website_url, 'lxml')

        # Extract the table
        SP_Table = html_site.find('table',{'class':'wikitable sortable'})
        
        # Extract the rows of the table
        rows = SP_Table.findAll('tr')
        
        # Extract for each row in rows the second value as this is the wanted symbol
        df = pd.DataFrame(columns=['Symbol', 'FullName', 'CSVName', 'Sector'])
        for row in rows[1:]:
            # Extract the company names
            companyFullName = row.findAll('td')[1].text
            # Extract the company csv names
            companyCSVName = companyFullName.replace('*', ' ')
            # Extract the company symbols
            companySymbol = row.findAll('td')[0].text
            companySymbol = ''.join(companySymbol.split())
            sector = row.findAll('td')[3].text
            df1 = pd.DataFrame([[companySymbol, companyFullName, companyCSVName, sector]], columns=df.columns)
            df = df.append(df1, ignore_index=True)
            
        df['Sector'] = df['Sector'].apply(lambda x: x.replace('\n', ''))
        df.to_csv(self.PATH_TO_COMPANY_FILES + '/Companies.csv', index=False)

        return
