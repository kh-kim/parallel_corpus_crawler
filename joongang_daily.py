import sys, time, codecs, re

from selenium import webdriver
from bs4 import BeautifulSoup

INTERVAL = 3

BASE_URL = 'http://koreajoongangdaily.joins.com'
URL = BASE_URL + '/news/list/List.aspx?gCat=060201&pgi=%d'
ARTICLE_SELECTOR = '#news_list > div > ul > li > dl > dt > a'
DATE_SELECTOR = 'div > ul > li > dl > dd > span'
TITLE_SELECTOR = '#sTitle_a'
OLD_CONTENT_SELECTOR = '#articlebody > div.article_dvleft > div > table > tbody > tr > td'
CONTENT_SELECTOR = 'div > div.article_content'
EXCLUDE_CONTENT_SELECTORS = ['div > div.article_content > b', 'div > div.article_content > font']
ALT_CONTENT_SELECTOR = '#articlebody > div.article_dvleft > div'
ALT_CONTENT_SELECTOR2 = '#articlebody > div.article_dvleft > div > p'

def get_content(url, driver_path):
    driver = webdriver.PhantomJS(driver_path)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    driver.close()
    time.sleep(INTERVAL)

    title = soup.select(TITLE_SELECTOR)[0].text.strip()
    print(len(soup.select(OLD_CONTENT_SELECTOR)), len(soup.select(CONTENT_SELECTOR)), len(soup.select(ALT_CONTENT_SELECTOR)))
    if len(soup.select(OLD_CONTENT_SELECTOR)) > 0:
        en_content = soup.select(OLD_CONTENT_SELECTOR)[0].text.strip()
        ko_content = soup.select(OLD_CONTENT_SELECTOR)[-1].text.strip()
    elif len(soup.select(CONTENT_SELECTOR)) > 0:
        en_content = soup.select(CONTENT_SELECTOR)[0].text.strip()
        ko_content = soup.select(CONTENT_SELECTOR)[1].text.strip()

        for selector in EXCLUDE_CONTENT_SELECTORS:
            for excluded in soup.select(selector):
                en_content = en_content.replace(excluded.text.strip(), '')
                ko_content = ko_content.replace(excluded.text.strip(), '')

    if (len(soup.select(CONTENT_SELECTOR)) == 0 or ko_content == '') and len(soup.select(ALT_CONTENT_SELECTOR)) > 0:
        en_content = soup.select(ALT_CONTENT_SELECTOR)[0].text.strip()
        ko_content = soup.select(ALT_CONTENT_SELECTOR)[-1].text.strip()

    en_content = re.sub('\\n', ' ', en_content).strip()
    ko_content = re.sub('\\n', ' ', ko_content).strip()

    if en_content == ko_content:
        ko_content = soup.select(ALT_CONTENT_SELECTOR2)[0].text.strip()
        ko_content = re.sub('\\n', ' ', ko_content)
        en_content = en_content[:-len(ko_content)]

    print(url)
    print(title)
    print(en_content)
    print(ko_content)
    print('')

    return title, en_content, ko_content

def get_article_urls(url, driver_path):
    driver = webdriver.PhantomJS(driver_path)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    print(len(soup.select(ARTICLE_SELECTOR)))
    print('\n'.join(['%d: %s\t%s' % (i, s.get('href').strip(), s.text.strip()) for i, s in enumerate(soup.select(ARTICLE_SELECTOR))]))
    articles = [s.get('href').strip() for s in soup.select(ARTICLE_SELECTOR)][-10:]
    
    driver.close()
    time.sleep(INTERVAL)

    return articles

def write(title, en, ko, output_fn):
    f = open(output_fn, 'a')

    f.write("%s\t%s\t%s\n" % (title, en, ko))

    f.close()

if __name__ == "__main__":
    output_fn = sys.argv[1]
    driver_path = './phantomjs'

    memory = []
    page_index = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    while True:
        url = URL % page_index
        print(url)
        article_urls = get_article_urls(url, driver_path)

        if len(article_urls) == 0:
            break
        
        for a_url in article_urls:
            try:
                title, en, ko = get_content(BASE_URL + a_url, driver_path)

                if title not in memory:
                    write(title, en, ko, output_fn)
            except Exception as e:
                print(e)

        page_index += 1
