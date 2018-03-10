import sys, time, codecs, re

from selenium import webdriver
from bs4 import BeautifulSoup

INTERVAL = 2
MAX_FAIL = 100
MAX_PAGE = 100
ALLOW_DUPLICATED = False

URL = 'http://endic.naver.com/search_example.nhn?sLn=kr&examType=example&query=%s&pageNo=%d'
TYPE_SELECTOR = 'ul > li > div > span'
TYPE_CLASS_VALUE = "fnt_k09"
SRC_SELECTOR = 'ul > li > div > input'
TGT_SELECTOR = 'ul > li > div > div > a'
TGT_CLASS_VALUE = "N=a:xmp.detail"

def get_stats(adds, memory, word_freq_map):
    freshs = []

    for a in adds:
        if memory.get(a) is None:
            memory[a] = 0
            freshs += [a]

            for w in a[1].lower().split(' '):
                word_freq_map[w] = 1 if word_freq_map.get(w) is None else (word_freq_map[w] + 1)

    return freshs, memory, word_freq_map

def get_next_word(word_freq_map, history):
    from operator import itemgetter
    
    candidates = sorted(word_freq_map.items(), key = itemgetter(1), reverse = True)
    
    for word, cnt in candidates:
        if word not in history:
            return word

    return None

def get_from_word(word, driver_path):
    collected = []

    for page_index in range(1, MAX_PAGE + 1):
        try:
            driver = webdriver.PhantomJS(driver_path)
            driver.get(URL % (word, page_index))
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            types = []
            for i, c in enumerate(soup.select(TYPE_SELECTOR)):
                if i % 2 == 0:
                    types += [c.text.strip()]
            src_sentences = [s.get('value').strip() for s in soup.select(SRC_SELECTOR)]
            tgt_sentences = [s.text.strip() for s in soup.select(TGT_SELECTOR)[4:]]
            
            collected += zip(types, src_sentences, tgt_sentences)

            print('%s(%d)' % (word, page_index))
            for c in zip(types, src_sentences, tgt_sentences):
                print("%s\t%s\t%s" % (c[0], c[1], c[2]))

            driver.close()
        except:
            print("Error on %s(%d)" % (word, page_index))
        time.sleep(INTERVAL)

    return collected

def write(collected, output_fn):
    f = open(output_fn, 'a')

    for c in collected:
        f.write("%s\t%s\t%s\n" % (c[0], c[1], c[2]))

    f.close()

if __name__ == "__main__":
    seed = sys.argv[1]
    output_fn = sys.argv[2]
    driver_path = './phantomjs'

    memory = {}
    word_freq_map = {}
    history = []

    word = seed
    while True:
        collected = get_from_word(word, driver_path)
        history += [word]
        freshs, memory, word_freq_map = get_stats(collected, memory, word_freq_map)
        word = get_next_word(word_freq_map, history)

        write(freshs, output_fn)

        if word is None:
            break