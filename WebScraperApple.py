from bs4 import BeautifulSoup
import requests
import urllib.parse
import asyncio
import json
from httpx import AsyncClient, Response
from typing import Dict, List
from loguru import logger as log
import re

#create a fake web browser to bypass the website's detection of automation
browser = AsyncClient(
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
    },
    follow_redirects=True,
    http2=False
)

#Extract data from Apple
async def AppleExtract(page_to_scrape: str) -> List[Dict]:
    #pull the Product Name, Price, and Link from the website
    def AppleOutput(response: Response) -> List[Dict]:
        soup = BeautifulSoup(response.text, "html.parser")
        AppleResults = []

        #extract the selector that contains all the product outputs using a dictionary and attributes
        AppleProducts = soup.find("div", attrs={"class":"rf-serp-results-tiles"})
        if not AppleProducts:
            return []
        
        AllAppleProducts = AppleProducts.find_all("div", attrs={"class":"rf-producttile small-6 large-4"})

        for item in AllAppleProducts:
            #extract the selector that contains the name of the product
            AppleName = item.select_one("h2", attrs={"class":"rf-producttitle-name"})
            #extract the price selector and the output
            ApplePriceExtract = item.select_one("span", attrs={"class":"rf-producttitle-pricecurrent"})
            #extract the selector that contains the link for the product
            AppleLinkExtract = item.find("a", attrs={"href":True}).get("href")
            AppleLink = f"https://www.apple.com/{AppleLinkExtract}" if AppleLinkExtract else None

            AppleResults.append({
                #"Apple Products" : AppleProducts.get_text(strip=True) if AppleProducts else None,
                "Product Name" : AppleName.get_text(strip=True) if AppleName else None,
                "Product Price" : ApplePriceExtract.get_text(" ", strip=True) if ApplePriceExtract else None,
                "Product Link" : AppleLink,
            })
        return AppleResults
    
    #build the website url by adding the product we want to find
    AppleUrl = "https://www.apple.com/us/search/" + urllib.parse.quote_plus(page_to_scrape)
    #wait for the repsonse from Apple
    response = await browser.get(AppleUrl)
    #check if Apple blocks the request
    if response.status_code == 403:
        raise Exception("Apple requests are blocked.")
    AppleData = AppleOutput(response)
    log.success(f"scraped",{len(AppleData)},"products from Apple")

    AppleData = [
        product for product in AppleData
        if product["Product Name"]
            and re.fullmatch(r"(?i)airpods 4", product["Product Name"].strip())
    ]

    return AppleData

async def SearchUp():
    AppleData = await AppleExtract(
        page_to_scrape = "Airpods 4"
    )

    # print the data in JSON format
    print(json.dumps(AppleData, indent=2))

if __name__=="__main__":
    asyncio.run(SearchUp())

async def ComparePrices (page_to_scrape: str):
    comparison = []
