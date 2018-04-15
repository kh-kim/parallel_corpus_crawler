import sys, time, codecs, re, os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from bs4 import BeautifulSoup

INTERVAL = 3
WAIT_UNTIL = 60

BASE_URL = 'http://english.chosun.com'
URL = 'http://english.chosun.com/svc/list_in/list.html?catid=%s&pn=%d'
CATEGORIES = ['1', 'F', '2', '3', '4', 'G'] 
# National/Politics, North Korea, Business, Sports, Entertainment, Health/Lifestyle

ARTICLE_SELECTOR = 'dl > dt > a'
KO_ARTICLE_SELECTOR = 'div > div > a'

ARTICLE_TITLE_ID = '#news_title_text_id'
ARTICLE_BODY = '#news_body_id > div > p'

KO_ARTICLE_TITLE_ID = '#news_title_text_id'
KO_ARTICLE_BODY = ['#news_body_id > div', '#article_2011']
EXCEPTIONS = ['영문으로 이 기사 읽기']

def get_article_urls(url, driver_path):
    print(url)

    driver = webdriver.PhantomJS(driver_path)
    try:
        #element = WebDriverWait(driver, WAIT_UNTIL).until(EC.presence_of_element_located((By.ID, "myDynamicElement")))
        driver.implicitly_wait(WAIT_UNTIL)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        articles = [s.get('href').strip() for s in soup.select(ARTICLE_SELECTOR)][:10]
        
        driver.close()

        time.sleep(INTERVAL)

        return articles
    except:
        driver.quit()        
        time.sleep(INTERVAL)
        
        return []

def get_article(url, driver_path):
    url = BASE_URL + url
    print(url)

    driver = webdriver.PhantomJS(driver_path)
    try:
        #element = WebDriverWait(driver, WAIT_UNTIL).until(EC.presence_of_element_located((By.ID, "myDynamicElement")))
        driver.implicitly_wait(WAIT_UNTIL)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        ko_article_url = None
        if len(soup.select(KO_ARTICLE_SELECTOR)) > 0 and soup.select(KO_ARTICLE_SELECTOR)[-1].text.strip().endswith('Korean'):
            ko_article_url = soup.select(KO_ARTICLE_SELECTOR)[-1].get('href').strip()

        title = soup.select(ARTICLE_TITLE_ID)[0].text.strip()

        contents = [s.text.strip() for s in soup.select(ARTICLE_BODY)]

        driver.close()
        time.sleep(INTERVAL)

        return title, contents, ko_article_url
    except:
        driver.quit()        
        time.sleep(INTERVAL)

        return None, None, None

def get_korean_article(url, driver_path):
    print(url)

    driver = webdriver.PhantomJS(driver_path)
    try:
        #element = WebDriverWait(driver, WAIT_UNTIL).until(EC.presence_of_element_located((By.ID, "myDynamicElement")))
        driver.implicitly_wait(WAIT_UNTIL)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        title = soup.select(KO_ARTICLE_TITLE_ID)[0].text.strip()

        if len(soup.select(KO_ARTICLE_BODY[0])) > 0:
            contents = []

            for c in [s.text.strip() for s in soup.select(KO_ARTICLE_BODY[0])][1:-1]:
                if c.strip() != "":
                    for s in c.strip().split('\n'):
                        if s.strip() != "" and not s.endswith('기자') and not s.startswith('#') and not s.endswith('특파원'):
                            contents += [s]

                            #print(KO_ARTICLE_BODY[0] + s)
        else:
            contents = []

            for c in [s.text.strip() for s in soup.select(KO_ARTICLE_BODY[1])][0].split('\n')[1:]:
                if c.strip() != "":
                    exception = False
                    for e in EXCEPTIONS:
                        if c.strip() == e:
                            exception = True
                            break
                    
                    if not exception:
                        contents += [c.strip()]

                        #print(KO_ARTICLE_BODY[1] + c)

        driver.close()
        time.sleep(INTERVAL)

        return title, contents
    except:
        driver.quit()
        time.sleep(INTERVAL)

        return None, None

def write(article_id, cat, title, content, ko_title = None, ko_content = None, dir_path = "./chosun/"):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    
    if not os.path.exists(dir_path + '/%s/' % cat):
        os.mkdir(dir_path + '/%s/' % cat)

    f = open(dir_path + '/%s/' % cat + article_id + '-en.txt', 'w')

    f.write(title + '\n')
    for c in content:
        f.write(c + '\n')

    f.close()

    if ko_title is not None and ko_content is not None:
        f = open(dir_path + '/%s/' % cat + article_id + '-ko.txt', 'w')

        f.write(ko_title + '\n')
        for c in ko_content:
            f.write(c + '\n')

        f.close()

if __name__ == "__main__":
    driver_path = './phantomjs'

    for category in CATEGORIES:
        page_index = 1

        while True:
            url = URL % (category, page_index)

            article_urls = get_article_urls(url, driver_path)
            
            if len(article_urls) == 0:
                break

            for article_url in article_urls:
                article_id = article_url.split('/')[-1].split('.')[0]
                title, content, ko_article_url = get_article(article_url, driver_path)

                print(article_id)
                print(title)
                print(content)

                ko_title, ko_content = None, None
                if ko_article_url is not None:
                    ko_title, ko_content = get_korean_article(ko_article_url, driver_path)

                    print(ko_title)
                    print(ko_content)
                
                if title is not None and content is not None:
                    write(article_id, category, title, content, ko_title, ko_content)

            page_index += 1