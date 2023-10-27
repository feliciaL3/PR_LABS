from bs4 import BeautifulSoup
import requests
import json


def extract_product_details(url):
    try:
        product_data = {}

        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        from unidecode import unidecode
        title = unidecode(soup.title.text)
        product_data['Title'] = title

        seller_info = soup.find("dl", class_="adPage__aside__stats__owner")
        if seller_info:
            seller = seller_info.text.strip()
            product_data['Seller'] = unidecode(seller)
        else:
            product_data['Seller'] = "Seller information not found"

        # Extract product description
        description_div = soup.find("div", class_="adPage__content__description grid_18")
        if description_div:
            description = description_div.get_text(separator=' ').strip()  # Get the text with cleaned-up whitespace
            product_data['Description'] = unidecode(description)
        else:
            product_data['Description'] = "Description not found"

        details_box = soup.find("div", class_="adPage__content__inner")

        price_ul = details_box.find("ul", class_="adPage__content__price-feature__prices")
        if price_ul:
            price_li = price_ul.find("li")
            formatted_price = unidecode(price_li.text.strip())
            product_data['Price'] = formatted_price

        # Extract properties
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

url = "https://999.md/ro/84708768"
print(extract_product_details(url))
