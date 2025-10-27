import requests
from bs4 import BeautifulSoup


def scrape():
    
    url = 'https://www.scrapethissite.com/pages/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    #print(soup)

    #finds all the <p> tags and extracts the content inside
    content=soup.find_all("p")
    print(content)

    scraped_info = f"{soup}_scrapedHTML.txt"

if __name__ == '__main__':
    scrape()