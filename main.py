import os
import argparse
import pdb
import shutil
from requests import get
from bs4 import BeautifulSoup
from time import sleep

current_dir = os.getcwd()

argument_parser = argparse.ArgumentParser(prog='kp-download',
                                          description='scrap through the given urls and download images and then create txt file for list of the products')

argument_parser.add_argument('-l', '--links', help='Provide n number of urls', nargs='*', required=True)
argument_parser.add_argument('-q', '--query',
                             help='provide query param e.g. page and it will be considered as follows: WEB_URL?QUERY=PAGE_INDEX. It defaults to: page',
                             default='page')
argument_parser.add_argument('-n', '--start', help='Starting index of the page query number default value is: 1',
                             nargs='*', type=int, default=[1])
argument_parser.add_argument('-m', '--end', help='Ending index of the page query number default value is: 1', nargs='*',
                             type=int, default=[1])
argument_parser.add_argument('-c', '--categories', help='Provide categories in which the respective url falls under.',
                             nargs='*', required=True)
argument_parser.add_argument('-p', '--products-container-selector',
                             help='Products container selector on the category page', required=True)
argument_parser.add_argument('-i', '--link-selector', help='Product link selector on a category page', required=True)
argument_parser.add_argument('-j', '--name-selector',
                             help='Product name selector within "link-selector" on a category page', required=True)
argument_parser.add_argument('-g', '--gallery-selector', help='Product image gallery selector on a product page',
                             required=True)
argument_parser.add_argument('-z', '--image-selector',
                             help='Product image selector within "--gallery-selector" on a product page', required=True)
argument_parser.add_argument('-o', '--output-dir',
                             help='Product image selector within "--gallery-selector" on a product page',
                             default=current_dir)

args = argument_parser.parse_args()

page_query_param = args.query

products_container_selector = args.products_container_selector
link_selector = args.link_selector
name_selector = args.name_selector
gallery_selector = args.gallery_selector
image_selector = args.image_selector
output_dir = args.output_dir


def get_soup(link):
    res = get(link)
    soup = BeautifulSoup(res.content, 'html.parser')
    return soup

def get_file(link):
    res = get(link, stream=True)
    return res

def write_err_log(file_path, page_link, err, product_name=None, product_link=None):
    file_path_length = len(file_path)
    pattern_symbol = '='
    half_pattern = pattern_symbol * int(file_path_length / 2)
    pattern = pattern_symbol * file_path_length
    with open(file_path, 'a') as file:
        file.write(pattern + '\n')
        file.write(half_pattern + page_link + half_pattern + '\n')

        if product_name:
            file.write(half_pattern + product_name + half_pattern + '\n')

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


details = zip(args.links, args.categories, args.start, args.end)

for category_link, category, page_start_index, page_end_index in details:
    domain = 'https://' + category_link.split("/")[2]
    print(f'Working on "{category} category"==========')
    os.mkdir(category)
    err_file = os.path.join(category, 'error.log')

    for page_idx in range(page_start_index, page_end_index + 1):
        link = category_link + "?" + page_query_param + "=" + str(page_idx)
        print(f'Working on "{link}"----------')
        page_soup = get_soup(link)
        wait_for_page()

        try:
            products_raw = get_element_from_selector(products_container_selector, page_soup).contents
            products = filter(lambda product: product != '\n',  products_raw)
        except IndexError as index_err_on_products:
            write_err_log(err_file, link, index_err_on_products)
            continue

        for product_item in products:
            product_anchor_tag = get_element_from_selector(link_selector, product_item)
            product_link = domain + product_anchor_tag.get('href')
            product_name = get_element_from_selector(name_selector, product_anchor_tag).get_text()
            product_folder = os.path.join(category, product_name.replace('/', '_'))
            try:
                os.mkdir(product_folder)
            except FileExistsError as file_exists_err:
                write_err_log(err_file, link, file_exists_err, product_name, product_link)
                continue

            print(f'Working on "{product_name}"**********')
            product_soup = get_soup(product_link)

            with open(os.path.join(product_folder, 'index.html'), 'w') as product_html_file:
                product_html_file.write(product_soup.prettify())

            wait_for_product()

            try:
                product_image_gallery_raw = get_element_from_selector(gallery_selector, product_soup).contents
                product_image_gallery = filter(lambda gallery_item: gallery_item != '\n',  product_image_gallery_raw)
            except IndexError as index_err:
                write_err_log(err_file,link,index_err,product_name,product_link)
                continue

            for img_idx, product_image_item in enumerate(product_image_gallery):
                product_image_tag = get_element_from_selector(image_selector, product_image_item)
                product_image_url = product_image_tag['src'].replace('//', 'https://')
                product_image_res = get_file(product_image_url)
                product_image_ext = product_image_res.headers['Content-Type'].split('/')[-1]
                product_image_name = os.path.join(product_folder, f'temp-{img_idx}.{product_image_ext}')

                wait_for_image()

                with open(product_image_name, 'wb') as image:
                    shutil.copyfileobj(product_image_res.raw, image)