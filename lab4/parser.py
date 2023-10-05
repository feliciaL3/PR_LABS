import socket
import json
from bs4 import BeautifulSoup

server_address = ('127.0.0.1', 8080)


def send_request(request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(server_address)
        client_socket.send(request.encode('utf-8'))
        response = client_socket.recv(4096).decode('utf-8')
    return response


def fetch_page_content(pages):
    page_content = {}
    for page in pages:
        http_request = f"GET {page} HTTP/1.1\r\nHost: {server_address[0]}\r\n\r\n"
        response = send_request(http_request)
        page_content[page] = response
    return page_content


def parse_product_page(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    product_details = {
        "name": soup.title.text.strip() if soup.title else "",
        "author": "Author not found",
        "price": 0.0,
        "description": "Description not found"
    }

    for p_element in soup.find_all('p'):
        p_text = p_element.text.strip()
        if p_text.startswith("Author:"):
            product_details["author"] = p_text.split(":", 1)[1].strip()
        elif p_text.startswith("Price:"):
            price_text = p_text.split(":", 1)[1].strip().replace('$', '')
            try:
                product_details["price"] = float(price_text)
            except ValueError:
                product_details["price"] = 0.0
        elif p_text.startswith("Description:"):
            product_details["description"] = p_text.split(":", 1)[1].strip()

    return product_details


def parse_product_listing_page(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    product_routes = [link.get('href') for link in soup.find_all('a') if link.get('href', '').startswith('/product/')]

    return product_routes


def save_content_to_files(page_content):
    for page, content in page_content.items():
        if "HTTP/1.1 200" in content:
            if page.startswith('/product/'):
                product_info = parse_product_page(content)
                formatted_content = json.dumps(product_info, indent=4)
            else:
                soup = BeautifulSoup(content, 'html.parser')
                relevant_text = soup.get_text()
                formatted_content = relevant_text.strip()

            with open(f"{page.strip('/').replace('/', '_')}.txt", 'w', encoding='utf-8') as file:
                file.write(formatted_content)


if __name__ == "__main__":
    pages_to_request = ['/', '/product', '/about', '/contacts']
    product_listing_page = fetch_page_content(['/product'])
    product_routes = parse_product_listing_page(product_listing_page['/product'])
    pages_to_request.extend(product_routes)
    page_content = fetch_page_content(pages_to_request)
    save_content_to_files(page_content)

    print("Content has been saved to text files.")
