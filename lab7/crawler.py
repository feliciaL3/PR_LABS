# Import necessary libraries
from bs4 import BeautifulSoup
import requests
import re

# Function to extract HTML document from a given URL
def getHTMLdocument(url):
    response = requests.get(url)
    return response.text


# Function to scrape car listings and return a list of links
def scrap(url_to_scrap, max_num_pag):
    car_links = []
    current_url = url_to_scrap
    html_document = getHTMLdocument(current_url)
    soup = BeautifulSoup(html_document, 'html.parser')
    current_page = soup.find('li', class_='current')
    page_number = current_page.a.text
    if int(page_number) > max_num_pag:
        return "max_num_page is reached"
    else:
        # Find all the anchor tags with "href" attribute starting with "/ro/" and "class" containing "js-item-ad"
        for link in soup.find_all('a', attrs={'href': re.compile("/ro/"), 'class': re.compile("js-item-ad")}):
            car_links.append("https://999.md" + link.get('href'))
        # Check if there is a next page link
        next_page_link = current_page.find_next('li').find('a') if current_page else None
        # If a next page link exists, extract and print the href attribute
        if next_page_link:
            next_page_url = "https://999.md" + next_page_link['href']
            scrap(next_page_url, max_num_pag)
        else:
            print("No next page link found.")
    return car_links
