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