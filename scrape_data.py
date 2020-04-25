import requests
from datetime import date
from bs4 import BeautifulSoup
import pandas as pd

headers = {"User-Agent":"Mozilla/5.0"}

def scrape_stats(p):
    try:
        year = str(date.today().year)
        r = requests.get("http://google.com/search?q="+p+" stats "+year+" transfermarkt")

        soup = BeautifulSoup(r.content,'html.parser')

        for link in soup.find_all("a"):
            if "stats" in link.text.lower() and "transfermarkt" in link.text.lower():
                search = link.get('href')
                break

        a = search.split('=')
        req = a[1]
        a = req.split('&')
        link = a[0]

        r1 = requests.get(link, headers = headers)

        soup = BeautifulSoup(r1.content,'html.parser')
        table = soup.find("table",attrs={"class":"items"})

        tbody = table.find("tbody")
        rows = tbody.find_all("td")

        df = pd.DataFrame(columns=['Competition','Games Played','Goals','Assists','YC','DYC','RC','MinutesPlayed'])

        row = [tr.text for tr in rows]
        count = 0
        l = []
        for e in row:
            count+=1
            l.append(e)
            if count == 9:
                l.pop(0)

                a_series = pd.Series(l, index = df.columns)
                df = df.append(a_series, ignore_index=True)

                l = []
                count = 0

        return df
    except:
        return None
