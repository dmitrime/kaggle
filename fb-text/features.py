import sys
import re
from collections import defaultdict
from math import log
from commons import *

class FeatureExtractor():

    def __init__(self, tags, D_train, D_test, freqsfile_train, freqsfile_test):
        #self.D_train = 6034195 # total documents in training
        #self.D_test = 845911 # total documents in test-rest
        self.D_train = D_train
        self.D_test = D_test

        # alldocs bodydocs titledocs word
        self.freqsfile_train = freqsfile_train
        self.freqsfile_test  = freqsfile_test

        self.tags = tags
        self.parse_freqs()

    def parse_freqs(self):
        self.freqs_train = defaultdict(dict)
        with open(self.freqsfile_train, 'r') as f:
            for line in f:
                vec = line.split()
                self.freqs_train[vec[3]] = {'all': int(vec[0]), 'body': int(vec[1]), 'title': int(vec[2])}

        self.freqs_test = defaultdict(dict)
        with open(self.freqsfile_test, 'r') as f:
            for line in f:
                vec = line.split()
                self.freqs_test[vec[3]] = {'all': int(vec[0]), 'body': int(vec[1]), 'title': int(vec[2])}

    def add_features(self, title, text, giventags):
        pos, neg = defaultdict(dict), defaultdict(dict)
        # First scan only the title
        for grams in next_token(title, True):
            # Better Gram parsing
            w, orig = None, None
            for gram, gram_orig in grams:
                if gram in self.tags:
                    w, orig = gram, gram_orig
            
            if w is not None:
                dct = pos if w in giventags else neg 
                if w not in dct: dct[w] = defaultdict(int)
                dct[w]['intitle'] = 1

        # Next, scan title and text
        count, prev = 1, None
        relfirst = -1
        for grams in next_token(text, True):
            w, orig = None, None
            for gram, gram_orig in grams:
                if gram in self.tags:
                    w, orig = gram, gram_orig

            if w is not None:
                dct = pos if w in giventags else neg
                if w not in dct: dct[w] = defaultdict(int)
                dct[w]['tf'] += 1
                dct[w]['punctuation'] = int(not orig.isalnum()) 
                dct[w]['digits'] = int(not orig.isalpha() and orig.isalnum()) 
                dct[w]['allcaps'] = int(orig.isupper())
                dct[w]['firstcaps'] = int(orig.istitle())
                dct[w]['dashed'] = int(orig.count('-') > 0)
                # first occurence in first 10% of text
                if 'relfirst' not in dct[w]:
                    dct[w]['relfirst'] = int(1.*count < 0.1*len(text))
                if prev is not None:
                    dct[w]['senstart'] = int(orig.istitle() and prev[-1] in '.?!:')
                dct[w]['senend'] = int(orig[-1] in '.?!:')
				# previous words
                dct[w]['inside'] = int('in' == prev or 'on' == prev or 'inside' == prev)
                dct[w]['using'] = int('using' == prev or 'use' == prev)
                dct[w]['with'] = int('with' == prev)
                dct[w]['link'] = int(orig.endswith('</a>'))
            count += 1
            prev = grams[0][1]

        #print "Given: ", giventags
        #print "Found: ", pos.keys()
        #print "Not found: ", giventags.difference(set(pos.keys()))
        #print
        return pos, neg

    def compute_test_features(self, inputfile, featurefile):
        # clear file
        open(featurefile, 'w').close()

        features = []
        for example, _ in self.compute_features(inputfile):
            idf = log((self.D_test+1.0) / (self.freqs_test[example['key']]['all']+1.0))
            example['tfidf'] = idf * example['tf']
            features.append(example)

            if len(features) >= 100000:
                self.output_features(features, featurefile, False, True)
                features = []
        self.output_features(features, featurefile, False, True)

    def compute_train_features(self, inputfile, featurefile):
        features = []
        for example, count in self.compute_features(inputfile):
            idf = log((self.D_train+1.0) / (self.freqs_train[example['key']]['all']+1.0))
            example['tfidf'] = idf * example['tf']
            features.append(example)
            if count >= self.D_train:
                break
        self.output_features(features, featurefile, True)

    def compute_features(self, inputfile):
        tfreq, bfreq = defaultdict(int), defaultdict(int)
        count = 0
        for id, title, body, giventags in read_train_data(inputfile):
            text = title + ' ' + body
            textlen = len(text)
            qpos, qneg = self.add_features(title.split(), text.split(), giventags)
            for (examples,is_pos) in [(qpos, True), (qneg, False)]:
                for key in examples.keys():
                    example = examples[key]
                    example['key'] = key
                    example['id'] = int(id)
                    example['positive'] = int(is_pos)
                    if 'relfirst' not in example:
                        example['relfirst'] = 0
                    example['tf'] = log(example['tf']) + 1.
                    yield example, count
            count += 1

    def output_features(self, examples, featurefile, is_training, append=False):
        stat = [0, 0]
        if append:
            out = open(featurefile, 'a')
        else:
            out = open(featurefile, 'w')

        for example in examples:
            if is_training: stat[example['positive']] += 1 

            features = (
                    example['key'],
                    example['tfidf'],
                    example['intitle'],
                    example['punctuation'],
                    example['digits'],
                    example['allcaps'],
                    example['firstcaps'],
                    example['dashed'],
                    example['senstart'],
                    example['senend'],
                    example['inside'],
                    example['using'],
                    example['with'],
                    example['link'],
                    example['relfirst'])

            pattern = "%s\t%f"
            for _ in range(len(features) - 2):
                pattern += "\t%d"
            out.write(pattern % features)

            if is_training:
                out.write("\t%d" % example['positive'])
            else:
                out.write("\t%d" % example['id'])
            out.write("\n")

        out.close()
        if is_training: 
            print stat

#build a set of tags and non-tags
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "usage: " + sys.argv[0] + " training.csv testing.csv"
        sys.exit()

    trainfile = sys.argv[1]
    testfile = sys.argv[2]

    freqsfile_train = 'data/frequency/frequency.train-13.5.csv'
    freqsfile_test  = 'data/frequency/frequency.test.csv'
    #freqsfile_train = 'data/frequency/frequency.train-6.7.csv'
    #freqsfile_test  = 'data/frequency/frequency.light.csv'

    # D_train about 120k samples, D_test number of lines
    #D_train, D_test= 6700, count_docs(testfile)-1 
    D_train, D_test= 13500, count_docs(testfile)-1 

    fe = FeatureExtractor(load_tags(), D_train, D_test, freqsfile_train, freqsfile_test)
    fe.compute_train_features(trainfile, 'data/features-train-13.5k.csv')
    fe.compute_test_features(testfile, 'data/features-test-full.csv')
    #fe.compute_train_features(trainfile, 'data/features-train-6.7k.csv')
    #fe.compute_test_features(testfile, 'data/features-test-light.csv')

