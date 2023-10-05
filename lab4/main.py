import json
import socket
import re
import requests

HOST = '127.0.0.1'
PORT = 8080


with open('products.json', 'r') as file:
    products = json.load(file)


home_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Home</title>
</head>
<body>
    <h1>Welcome to the Home Page</h1>
</body>
</html>
"""

contacts_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Home</title>
</head>
<body>
    <h1>Welcome to the Contacts Page</h1>
    <h1>our number : 0348374 845 454 </h1>

</body>
</html>
"""

product_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Products</title>
</head>
<body>
    <h1>Name</h1>
    <p>Something</p>
</body>
</html>
"""

about_page = """
<!DOCTYPE html>
<html>
<head>
    <title>About Us</title>
</head>
<body>
    <h1>About Us</h1>
    <p>AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH. Buna ziua</p>
</body>
</html>
"""

product_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{name}</title>
</head>
<body>
    <h1>{name}</h1>
    <p>Author: {author}</p>
    <p>Price: ${price}</p>
    <p>Description: {description}</p>
</body>
</html>
"""

def handle_request(request):
    if request == '/':
        return home_page, 200
    elif request == '/about':
        return about_page, 200

    elif request == '/contacts':
        return contacts_page, 200
    elif request == '/product-listing':
        return product_page, 200
    elif re.match(r'/product/(\d+)', request):
        product_id = int(re.match(r'/product/(\d+)', request).group(1))
        if 0 <= product_id < len(products):
            product = products[product_id]
            return product_template.format(**product), 200
        else:
            return 'Product not found', 404
    elif request == '/product':
        return product_listing_page(), 200
    else:
        return '404 Page Not Found', 404

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Server is running on http://{HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        data = client_socket.recv(1024).decode('utf-8')

        if not data:
            continue

        request_lines = data.split('\r\n')

        first_line = request_lines[0]
        method, request = first_line.split(' ')[0], first_line.split(' ')[1]

        response, status_code = handle_request(request)

        response_headers = f"HTTP/1.1 {status_code}\r\nContent-Type: text/html\r\n"
        response_data = f"{response_headers}\r\n{response}\r\n"

        client_socket.sendall(response_data.encode('utf-8'))
        client_socket.close()


def product_listing_page():
    listing = "<h1>Products</h1>"
    listing += "<ul>"
    for idx, product in enumerate(products):
        listing += f"<li><a href='/product/{idx}'>{product['name']}</a></li>"
    listing += "</ul>"
    return listing

if __name__ == "__main__":
    run_server()
