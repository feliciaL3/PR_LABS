from bs4 import BeautifulSoup
import requests
import json


def extract_product_details(url):
    try:
        product_data = {}

        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # extract the product title
        from unidecode import unidecode
        title = unidecode(soup.title.text)
        product_data['Title'] = title

        details_box = soup.find("div", class_="adPage__content__inner")

        price_ul = details_box.find("ul", class_="adPage__content__price-feature__prices")
        if price_ul:
            price_li = price_ul.find("li")
            formatted_price = unidecode(price_li.text.strip())
            product_data['Price'] = formatted_price

        # extract properties
        properties_div = details_box.find("div", class_="adPage__content__features")
        property_items = properties_div.find_all("li")

        for item in property_items:
            key_element = item.find("span", class_="adPage__content__features__key")
            key = unidecode(key_element.text.strip())

            value_element = item.find("span", class_="adPage__content__features__value")
            value = unidecode(value_element.text.strip()) if value_element else "Present"

            product_data[key] = value

        category_container = details_box.find("div", class_="adPage__content__features adPage__content__features__category")
        if category_container:
            category_element = category_container.find("div").find("div")
            category_text = unidecode(category_element.text.strip())
            product_data['Category'] = category_text
        else:
            product_data['Category'] = "Category Not Found"



        json_data = json.dumps(product_data, indent=4, ensure_ascii=False, separators=(',', ':')).replace('"', '')

        return json_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

url = "https://999.md/ro/82988148"
print(extract_product_details(url))
