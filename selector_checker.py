import sys, time, codecs, re

from selenium import webdriver
from bs4 import BeautifulSoup

DRIVER_PATH = './phantomjs'

# You should change these.
URL = 'http://news.chosun.com/site/data/html_dir/2017/05/25/2017052500251.html'
SELECTOR = '#news_body_id > div'

driver = webdriver.PhantomJS(DRIVER_PATH)
driver.get(URL)
soup = BeautifulSoup(driver.page_source, 'html.parser')

results = soup.select(SELECTOR)

for i, result in enumerate(results):
    # You can commentize or uncommentize these.

    print("%d\t" % (i + 1) + result.text.strip())
    #print("%d\t" % (i + 1) + result.get('href').strip())
    #print("%d\t" % (i + 1) + result.get('id').strip())