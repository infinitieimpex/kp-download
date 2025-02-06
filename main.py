import os
import argparse
import shutil
from requests import get
from bs4 import BeautifulSoup
from time import sleep

current_dir = os.getcwd()

argument_parser = argparse.ArgumentParser(prog='kp-download', description='scrap through the given urls and download images and then create txt file for list of the products')

argument_parser.add_argument('-l', '--links', help='Provide n number of urls', nargs='*', required=True)
argument_parser.add_argument('-q', '--query', help='provide query param e.g. page and it will be considered as follows: WEB_URL?QUERY=PAGE_INDEX. It defaults to: page', default='page')
argument_parser.add_argument('-n', '--start', help='Starting index of the page query number default value is: 1', nargs='*', type=int, default=[1])
argument_parser.add_argument('-m', '--end', help='Ending index of the page query number default value is: 1', nargs='*', type=int, default=[1])
argument_parser.add_argument('-c', '--categories', help='Provide categories in which the respective url falls under.', nargs='*', required=True)
argument_parser.add_argument('-p', '--products-container-selector', help='Products container selector on the category page', required=True)
argument_parser.add_argument('-i', '--link-selector', help='Product link selector on a category page', required=True)
argument_parser.add_argument('-j', '--name-selector', help='Product name selector within "link-selector" on a category page', required=True)
argument_parser.add_argument('-g', '--gallery-selector', help='Product image gallery selector on a product page', required=True)
argument_parser.add_argument('-q', '--image-selector', help='Product image selector within "--gallery-selector" on a product page', required=True)
argument_parser.add_argument('-o', '--output-dir', help='Product image selector within "--gallery-selector" on a product page', default=current_dir)

args = argument_parser.parse_args()

page_query_param = args.query

def get_soup(link):
    res = get(link)
    soup = BeautifulSoup(res.content)
    return soup

def write_err_log(file_path, page_link, err, product_name=None, product_link=None):
    file_path_length = len(file_path)
    pattern_symbol = '='
    half_pattern = pattern_symbol * (file_path_length / 2)
    pattern = pattern_symbol * file_path_length

    with open(file_path, 'w') as file:
        file.write(pattern + '\n')
        file.write(half_pattern + page_link + half_pattern + '\n')

        if product_name:
            file.write(half_pattern + product_name + half_pattern)

        if product_link:
            file.write(f'Product Link: {product_link}\n')

        file.write(str(err) + '\n')

        if not product_link:
            file.write('Above error occurred on page index level\n')

        file.write(pattern + '\n\n')

PAGE_SLEEP_BETWEEN_REQUESTS = 3
PRODUCT_SLEEP_BETWEEN_REQUESTS = 3
IMAGE_SLEEP_BETWEEN_REQUESTS = 1

def wait_for_page():
    sleep(PAGE_SLEEP_BETWEEN_REQUESTS)

def wait_for_product():
    sleep(PRODUCT_SLEEP_BETWEEN_REQUESTS)

def wait_for_image():
    sleep(IMAGE_SLEEP_BETWEEN_REQUESTS)

def get_element_from_selector(selector, soup):
    element = soup.select(selector)[0]
    return element

