import requests
from bs4 import BeautifulSoup


def scrape_links(max_pag, current_page, page_urls, found_urls):
    base_url = "https://999.md"
    current_page_url = page_urls[current_page]

    response = requests.get(current_page_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # verifica parcurgerea tuturor linkurilor de pe pagina
    # si  ignora booster
    for anchor in soup.find_all('a', href=lambda href: href and not href.startswith('/b'), class_='js-item-ad'):
        link_href = anchor.get('href')
        complete_url = base_url + link_href
        found_urls.add(complete_url)

    # select elements that match the CSS selector 'nav.paginator > ul > li > a.'
    # extract pagination links and eliminate duplicates
    pagination_links = set(base_url + page_link['href'] for page_link in soup.select('nav.paginator > ul > li > a'))
    page_urls.extend(link for link in pagination_links if link not in page_urls)

    #daca am ajuns la limit pages
    if current_page == max_pag or current_page >= len(page_urls) - 1:
        return found_urls

    return scrape_links(max_pag, current_page + 1, page_urls, found_urls)

# initial_page_urls = ["https://999.md/ro/list/clothes-and-shoes/wedding-shoes"]
initial_page_urls = ["https://999.md/ro/list/clothes-and-shoes/hats"]
collected_links = scrape_links(500, 0, initial_page_urls, set())

with open('links.txt', 'w') as file:
    file.writelines(link + '\n' for link in collected_links)

for i, link in enumerate(collected_links, start=1):
    print(f"{i}. {link}")
