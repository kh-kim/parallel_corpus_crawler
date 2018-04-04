import sys, time, codecs, re
import numpy as np

from selenium import webdriver
from bs4 import BeautifulSoup

NO_CONTENT_ALLOW_THRES = 5
INTERVAL = 2
MAX_FAIL = 100
MAX_PAGE = 100
ALLOW_DUPLICATED = False

URL = 'http://endic.naver.com/search_example.nhn?sLn=kr&examType=example&query=%s&pageNo=%d'
DOMAIN_SELECTOR = 'ul > li > div > span.fnt_k09'
SRC_SELECTOR = 'ul > li > div > input'
TGT_SELECTOR = 'ul > li > div.mar_top1'

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

def get_next_word(word_freq_map, history, show = True):
    from operator import itemgetter
    
    candidates = sorted(word_freq_map.items(), key = itemgetter(1), reverse = True)
    
    to_print = []
    for word, cnt in candidates:
        to_print += [(word, cnt)]
        if word not in history:
            if show:
                for word, cnt in to_print[-10:]:
                    print('%s\t%d' % (word, cnt))

            return word
            
    return None

def get_from_word(word, driver_path):
    collected = []
    zero_cnt = 0

    for page_index in range(1, MAX_PAGE + 1):
        driver = webdriver.PhantomJS(driver_path)
        driver.get(URL % (word, page_index))
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        confidences = []
        types = [s.text.strip() for s in soup.select(DOMAIN_SELECTOR)]
        src_sentences = [s.get('value').strip() for s in soup.select(SRC_SELECTOR)]
        tgt_sentences = []

        '''
        print(len(types), len(src_sentences), len(soup.select(TGT_SELECTOR)))
        for i, c in enumerate(soup.select('ul > li > div.mar_top1')):
            if '\n' not in c.text.strip():
                print(i, c.text.strip())
            else:
                for j, t in enumerate(c.text.strip().split('\n')):
                    print(i, j, t)
                    '''

        for c in soup.select(TGT_SELECTOR):
            if '\n' in c.text.strip():
                if len(c.text.strip().split('\n')) >= 11:
                    tgt_sentences += [c.text.strip().split('\n')[11]]
                    confidences += [1]
                else:
                    tgt_sentences += ['']
                    confidences += [0]
            if '\n' not in c.text.strip():
                tgt_sentences += [c.text.strip()]
                confidences += [2]

        if len(confidences) == 0 or np.sum(confidences) == 0:
            if zero_cnt > NO_CONTENT_ALLOW_THRES:
                break
            zero_cnt += 1
        else:
            zero_cnt = 0
        
        collected += zip(confidences, types, src_sentences, tgt_sentences)

        print('%s(%d)' % (word, page_index))
        for c in zip(confidences, types, src_sentences, tgt_sentences):
            print("%d\t%s\t%s\t%s" % c)

        driver.close()
        time.sleep(INTERVAL)

    return collected

def write(collected, output_fn):
    f = open(output_fn, 'a')

    for c in collected:
        f.write("%d\t%s\t%s\t%s\n" % c)

    f.close()

def read(fn):
    collected = []

    try:
        f = open(fn, 'r')
    
        for line in f:
            if line.strip() != "":
                tokens = line.strip().split('\t')
                tokens[0] = int(tokens[0])

                collected += [tuple(tokens)]

        f.close()
    except:
        pass

    return collected

if __name__ == "__main__":
    seed = sys.argv[1]
    output_fn = sys.argv[2]
    driver_path = './phantomjs'

    memory = {}
    word_freq_map = {}
    history = []

    collected = read(output_fn)
    print('Read %d sentences' % len(collected))
    freshs, memory, word_freq_map = get_stats(collected, memory, word_freq_map)
    
    while True:
        next_word = get_next_word(word_freq_map, history, show = False)

        if len(collected) == 0:
            break

        if next_word == seed:
            print('\t'.join(history))
            break
        else:
            history += [next_word]
    

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
