import sys, time, codecs, re

from selenium import webdriver
from bs4 import BeautifulSoup

DRIVER_PATH = './phantomjs'

# You should change these.
URL = 'http://english.chosun.com/svc/list_in/list.html?catid=G&pn=1'
SELECTOR = '#exampleAjaxArea > ul > li > div.mar_top1'
SELECTOR = '#exampleAjaxArea > ul > li.utb'
SELECTOR = '#list_area > dl > dt > a'

driver = webdriver.PhantomJS(DRIVER_PATH)
driver.get(URL)
soup = BeautifulSoup(driver.page_source, 'html.parser')

results = soup.select(SELECTOR)

for br in soup.find_all('br'):
    br.replace_with('\n')

for i, result in enumerate(results):
    # You can commentize or uncommentize these.

    #print("%d\t" % (i + 1) + result.text.strip())
    #print("(%d)\n" % (i + 1) + "\n".join(["%d\t%s" % (j, s) for j, s in enumerate(result.text.strip().split('\n'))]))
    print("%d\t" % (i + 1) + result.get('href').strip())
    #print("%d\t" % (i + 1) + result.get('value').strip())
