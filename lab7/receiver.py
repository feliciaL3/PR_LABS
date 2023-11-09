# receiver.py
from threading import Thread, Lock
from tinydb import TinyDB
import requests
import pika
import bs4

# initialize tinydb for storing scraped data
db = TinyDB('scapped_data.json', indent=4, separators=(',', ': '), ensure_ascii=False, encoding='utf-8')
lock = Lock()


def scraper(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        title = soup.find('header', {"class": "adPage__header"}).text

        price_element = soup.find('span', {"class": "adPage__content__price-feature__prices__price__value"})
        if price_element:
            price = price_element.text
        else:
            price = "Price not found"

        currency_element = soup.find('span', {"class": "adPage__content__price-feature__prices__price__currency"})
        if currency_element:
            currency = currency_element.text
        else:
            currency = ""

        description_element = soup.find('div',
                                        {"class": "adPage__content__description grid_18", "itemprop": "description"})
        if description_element:
            description = description_element.text
        else:
            description = " no description found "

        return {
            'TITLE': title,
            'PRICE': price + currency,
            'DESCRIPTION': description,
        }

    else:
        print(f"ERROR Unable to retrieve the web page  at {url}. Status code: {response.status_code}")
        return None


def callback(ch, method, properties, body, thread_num):
    url = body.decode()     # callback function to process a message from the queue
    scraped_data = scraper(url)

    if scraped_data:
        with lock:   # insert scraped data into TinyDB
            db.insert(scraped_data)
        print(f"Thread {thread_num}: Processing URL - {url}")


def process_data_from_queue(thread_num):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='url_queue')
    channel.basic_consume(queue='url_queue', on_message_callback=lambda ch, method, properties, body: callback(ch,
                                                                                                               method,
                                                                                                               properties,
                                                                                                               body,
                                                                                                               thread_num),
                          auto_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    num_threads = 6

    print(f'{num_threads} threads are processing urls at the same time.')
    threads = []
    # start threads to process data from the queue
    for i in range(num_threads):
        thread = Thread(target=process_data_from_queue, args=(i,))
        thread.start()
        threads.append(thread)

    # wait for all threads to finish
    for thread in threads:
        thread.join()
