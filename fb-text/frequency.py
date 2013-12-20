import sys
import re
from collections import defaultdict
from commons import *

def frequency(words, tags, freq):
    fq = defaultdict(int)
    for grams in next_token(words):
        for gram in grams:
            if gram in tags:
                fq[gram] += 1
    for key in fq.keys():
        freq[key] += 1

def compute_frequency(infile, freqfile, tags, limit=None):
    afreq, tfreq, bfreq = defaultdict(int), defaultdict(int), defaultdict(int)
    with open(infile, 'r') as f:
        #skip first
        f.readline()
        count = 0
        for line in f:
            parts = line.strip(' ').strip('\n').strip('"').split('","', 2)
            if len(parts) < 3: continue
            id, title, rest = parts
            comma = rest.rfind(',')
            body, giventags = stripcode(rest[:comma-1]), rest[comma+2:]

            frequency(title.split(), tags, tfreq)
            frequency(body.split(), tags, bfreq)
            frequency(title.split()+body.split(), tags, afreq)

            if limit and count >= limit:
                break

            count += 1

    out = open(freqfile, 'w')
    taglist = [ [afreq[w], bfreq[w], tfreq[w], w] for w in tags.keys() ]
    taglist = sorted(taglist, key = lambda x: x[0], reverse=True)
    for line in taglist:
        out.write("%d\t%d\t%d\t%s\n" % (line[0], line[1], line[2], line[3]))
    out.close()

if __name__ == '__main__':
    #build a set of tags and non-tags
    #if len(sys.argv) < 2:
        #print "usage: " + sys.argv[0] + " input.csv"
        #sys.exit()

    infile_train = 'data/TrainProc.csv'
    infile_test = 'data/TestRest.csv'
    infile_light = 'data/LightValidationProc.csv'
    tagsfile = 'data/tags.csv'
    #freqfile = 'data/frequency.test.csv'
    
    tags = load_tags(tagsfile)
    compute_frequency(infile_train, 'data/frequency.train.csv', tags, limit=13500)
    #compute_frequency(infile_test, 'data/frequency.test.csv', tags)
    #compute_frequency(infile_light, 'data/frequency.light.csv', tags)

