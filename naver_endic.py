import sys, time, codecs, re

from selenium import webdriver
from bs4 import BeautifulSoup

INTERVAL = 2
MAX_FAIL = 100
MAX_PAGE = 100
ALLOW_DUPLICATED = False

URL = 'http://endic.naver.com/search_example.nhn?sLn=kr&examType=example&query=%s&pageNo=%d'
DOMAIN_SELECTOR = 'ul > li > div > span.fnt_k09'
SRC_SELECTOR = 'ul > li > div > input'
TGT_SELECTOR = 'ul > li > div > div > a'

def get_stats(adds, memory, word_freq_map):
    freshs = []

    for a in adds:
        if memory.get(a) is None:
            memory[a] = 0
            freshs += [a]

            for w in a[2].lower().split(' '):
                w = re.sub('(\\.|,|\\?|!|\\(|\\))', '', w)
                word_freq_map[w] = 1 if word_freq_map.get(w) is None else (word_freq_map[w] + 1)

    return freshs, memory, word_freq_map

def get_next_word(word_freq_map, history):
    from operator import itemgetter
    
    candidates = sorted(word_freq_map.items(), key = itemgetter(1), reverse = True)
    
    to_print = []
    for word, cnt in candidates:
        to_print += [(word, cnt)]
        if word not in history:
            return word

    for word, cnt in to_print[-10:]:
        print('%s\t%d' % (word, cnt))

    return None

def get_from_word(word, driver_path):
    collected = []

    for page_index in range(1, MAX_PAGE + 1):
        driver = webdriver.PhantomJS(driver_path)
        driver.get(URL % (word, page_index))
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        confidences = []
        types = [s.text.strip() for s in soup.select(DOMAIN_SELECTOR)]
        src_sentences = [s.get('value').strip() for s in soup.select(SRC_SELECTOR)]
        tgt_sentences = []

        is_user = False
        for c in soup.select(TGT_SELECTOR)[4:]:
            if '\n' in c.text:
                is_user = True
            if ("\n" not in c.text) and c.text.strip()[0] != '|':
                tgt_sentences += [c.text.strip()]
                confidences += [0 if is_user else 1]
                is_user = False
        
        collected += zip(confidences, types, src_sentences, tgt_sentences)

        print('%s(%d)' % (word, page_index))
        for c in zip(confidences, types, src_sentences, tgt_sentences):
            print("%d\t%s\t%s\t%s" % c)

        driver.close()
        time.sleep(INTERVAL)

        if len(collected) == 0:
            break

    return collected

def write(collected, output_fn):
    f = open(output_fn, 'a')

    for c in collected:
        f.write("%d\t%s\t%s\t%s\n" % c)

    f.close()

def read(fn):
    collected = []

    f = open(fn, 'r')

    for line in f:
        if line.strip() != "":
            collected += [line.strip().split('\t')]

    f.close()

    return collected

if __name__ == "__main__":
    seed = sys.argv[1]
    output_fn = sys.argv[2]
    driver_path = './phantomjs'

    memory = {}
    word_freq_map = {}
    history = []

    try:
        collected = read(output_fn)
        print('Read %d sentences' % len(collected))
        freshs, memory, word_freq_map = get_stats(collected, memory, word_freq_map)
    except:
        pass

    word = seed
    while True:
        collected = get_from_word(word, driver_path)
        history += [word]
        freshs, memory, word_freq_map = get_stats(collected, memory, word_freq_map)
        print('%d/%d sentences are not duplicated. (total: %d)' % (len(freshs), len(collected), len(memory)))

        word = get_next_word(word_freq_map, history)

        write(freshs, output_fn)

        if word is None:
            break