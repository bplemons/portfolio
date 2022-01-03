from bs4 import BeautifulSoup
import requests
import csv
import re


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36", "Accept-Encoding": "gzip, deflate",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}

url = f'https://www.realtor.com/realestateandhomes-search/Yukon_OK/beds-3/baths-2/type-single-family-home/pnd-hide/nc-hide/pg-'

houseList = []

class House:
    def __init__(self, address, price, link, bed, bath, sqft):
        self.address = address
        self.price = price
        self.link = link
        self.beds = bed
        self.baths = bath
        self.sqft = sqft


# return the html for a given url
def getpage(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    soup2 = BeautifulSoup(soup.prettify(), "html.parser")
    return soup2


# check for next page in paginated results
# if link to next page exists, return true
def getnextpage(soup):
    page = soup.find('div', class_='pagination-wrapper')
    links = page.find_all('a', class_='item btn disabled')
    if not links:
        return True
    else:
        for link in links:
            if 'Next' in link.text:
                return False
            else:
                return True


# scrape the house data from the page
def scrapePage(soup):
    houses = soup.find_all('div', class_='type-srp-result')
    for house in houses:
        price = house.find('div', class_='srp-page-price').find('span', class_='bowEcH').text
        price = re.sub('\s{1,}', ' ', price)
        address = house.find(
            'div', class_='srp-page-address').text.replace(',', '')
        address = re.sub('\s{2,}', ' ', address)
        link = 'https://www.realtor.com' + \
            str(house.find('div', class_='photo-wrap').find('a')['href'])

        details = house.find_all('li', class_='srp_list')
        detailDict = {}
        for detail in details:
            label = detail.find('span', class_='meta-label').text.strip()
            value = detail.find(
                'span', class_='meta-value').text.replace(',', '').strip()
            detailDict[label] = value

        houseList.append(House(
            address, price, link, detailDict['bed'], detailDict['bath'], detailDict['sqft']))


def saveToFile():
    with open('realtor_results.csv', 'w',) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Price', 'Bed', 'Bath', 'Sqft', 'Link'])
        for house in houseList:
            writer.writerow([house.price, house.beds,
                            house.baths, house.sqft, house.link])


# build url, get the page, scrape the page, repeat for each page, save to csv
i = 0
while True:
    i += 1
    num = str(i)
    newUrl = url + num
    print(newUrl)
    soup = getpage(newUrl)
    scrapePage(soup)
    res = getnextpage(soup)
    if not res:
        saveToFile()
        print('Finished')
        break
