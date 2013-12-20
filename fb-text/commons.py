import re
from collections import defaultdict

def make_patterns(patterns, htmltags):
    def decorate(func):
        pats = []
        for htmltag in htmltags:
            pats.append(re.compile("<"+htmltag+">.*?</"+htmltag+">"))
        pats.append(re.compile('<[a-z]+?>'))
        pats.append(re.compile('</[a-z]+?>'))
        setattr(func, patterns, pats)
        return func
    return decorate

@make_patterns("patterns", ['pre', 'code'])
def stripcode(body):
    for pat in stripcode.patterns:
        body = pat.sub('', body)
    return body

def read_train_data(filename):
    with open(filename, 'r') as f:
        f.readline() #skip first
        for line in f:
            parts = line.strip(' ').strip('\n').strip('"').split('","', 2)
            if len(parts) < 3: continue
            idd, title, rest = parts
            comma = rest.rfind(',')
            body, giventags = stripcode(rest[:comma-1]), set(rest[comma+2:].split())

            yield idd, title, body, giventags

def load_stops(fname='data/english.stop'):
    stops = set()
    with open(fname, 'r') as f:
        for line in f:
            stops.add(line.strip())
    return stops

def load_tags(fname='data/tags.csv'):
    tags = defaultdict(int)
    with open(fname, 'r') as f:
        for line in f:
            count, word = line.split()
            tags[word] = int(count)
    return tags

def load_freqs(fname='data/frequency.csv'):
    freqs = defaultdict(int)
    with open(fname, 'r') as f:
        for line in f:
            acount, bcount, tcount, word = line.split()
            freqs[word] = (int(acount), int(bcount), int(tcount))
    return freqs

def load_intersection(fname):
	res = dict()
	with open(fname) as f:
		for line in f:
			idd, tags = line.split(',')
			res[idd] = tags.strip()
	return res

def load_correlated(fname):
	res = defaultdict(list)
	with open(fname) as f:
		for line in f:
			tag, tags = line.split()
			res[tag] = tags.split(',')
	return res

def count_docs(fname):
    count = 0
    with open(fname) as f:
        for line in f:
            count += 1
    return count

def bag_words(title, body, stops):
    text = title + ' ' + body
    words = text.split()
    words = filter(lambda w: w not in stops, map(process_word, words))
    return filter(lambda w: w and '/' not in w and '"' not in w and '\\' not in w and not w.isdigit() and ',' not in w, words)

def process_word(word):
    word = word.lower()
    #pat_open=re.compile('<[a-z]+?>')
    #pat_close=re.compile('</[a-z]+?>')
    #word = pat_open.sub('', word)
    #word = pat_close.sub('', word)
    word = word.rstrip('.') # keep .net and not net.
    word = word.lstrip('+#') # keep c++ and not ++c
    return word.strip('!"$%&\'()*,/:;<=>?@[\\]^`{|}~-_') # keep +, #

def next_token(words, add_orig=False, add_position=False):

    def word_tokens(word, word_orig, grams, grams_orig):
        # split on .
        pos = word.find('.')
        if pos != -1:
            grams.append(word[:pos] + '-' + word[pos+1:])
            grams_orig.append(word_orig)

        # split on /
        pos = word.find('/')
        if pos != -1 and 'http' not in word and '.com' not in word:
            parts = word.split('/', 1)
            parts_orig = word_orig.split('/', 1)
            if parts[0] and parts[1] and parts_orig[0] and parts_orig[1]:
                grams.append('-'.join(parts))
                grams_orig.append(word_orig)
                grams.extend(parts)
                grams_orig.extend(parts_orig)

        # split on ,
        pos = word.find(',')
        if pos != -1:
            if word_orig[0] == ',': word_orig = word_orig[1:]
            if word_orig[-1] == ',': word_orig = word_orig[:-1]
            parts = word.split(',', 1)
            parts_orig = word_orig.split(',', 1)
            if parts[0] and parts[1] and parts_orig[0] and parts_orig[1]:
                grams.append('-'.join(parts))
                grams_orig.append(word_orig)
                grams.extend(parts)
                grams_orig.extend(parts_orig)

    prev, pprev = None, None
    prev_orig, pprev_orig = None, None
    for i in range(len(words)):
        word = process_word(words[i])
        word_orig = words[i]

        if word == '': continue

        twogram, threegram = '', ''
        twogram_orig, threegram_orig = '', ''
        grams, grams_orig = [word], [word_orig]

        word_tokens(word, word_orig, grams, grams_orig)

        if prev:
            twogram1 = prev + "-" + word
            twogram2 = word + "-" + prev
            twogram1_orig = prev_orig + " " + word_orig
            twogram2_orig = word_orig + " " + prev_orig
            grams.append(twogram1)
            grams.append(twogram2)
            grams_orig.append(twogram1_orig)
            grams_orig.append(twogram2_orig)
        if pprev:
            grams.append(pprev + "-" + twogram1)
            grams.append(twogram1 + "-" + pprev)
            grams.append(pprev + "-" + twogram2)
            grams.append(twogram2 + "-" + pprev)
            grams.append(word + "-" + pprev + "-" + prev)
            grams.append(prev + "-" + pprev + "-" + word)

            grams_orig.append(pprev_orig + " " + twogram1_orig)
            grams_orig.append(twogram1_orig + " " + pprev_orig)
            grams_orig.append(pprev_orig + " " + twogram2_orig)
            grams_orig.append(twogram2_orig + " " + pprev_orig)
            grams_orig.append(word_orig + "-" + pprev_orig + "-" + prev_orig)
            grams_orig.append(prev_orig + "-" + pprev_orig + "-" + word_orig)

        pprev = prev
        prev = word

        pprev_orig = prev_orig
        prev_orig = word_orig

        if add_orig:
            if add_position:
                c = i+1 
                yield zip(grams, grams_orig, [c]*len(grams))
            else:
                yield zip(grams, grams_orig)
        else:
            yield grams

