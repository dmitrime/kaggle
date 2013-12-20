import sys
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from collections import defaultdict
from time import time
from commons import *

class TagBagger:
    def __init__(self, wordbag='data/clusterbag.csv'):
        self.clusters = dict()
        with open(wordbag) as f:
            for line in f:
                tags, words = line.split('\t')
                self.clusters[tuple(tags.split(','))] = set(words.split(','))

    def rank(self, example):
        score, best_tags = 0.0, []
        for tags, words in self.clusters.items():
            #inter = len(example.intersection(words))
            #union = len(example.union(words))
            #jaccard = float(inter)/float(union)
            jaccard = len(example.intersection(words))
            if jaccard > score:
                score = jaccard
                best_tags = tags
        return list(best_tags)

class TagSelector:
    def __init__(self, trainfeatures, tags):
        words, samples, targets = [], [], []
        positive = 0
        for word, sample, target in self.parse_features(trainfeatures, True):
            words.append(word)
            samples.append(sample)
            targets.append(target)

            # balanced set 
            #if target == 1:
                #words.append(word)
                #samples.append(sample)
                #targets.append(target)
                #positive += 1
            #elif positive > 0:
                #words.append(word)
                #samples.append(sample)
                #targets.append(target)
                #positive = max(positive-1, 0)
                
        samples, targets = np.array(samples), np.array(targets)

        #self.scaler = StandardScaler()
        #samples = self.scaler.fit_transform(samples)

        start_t = time()
        self.logit_fit = LogisticRegression().fit(samples, targets)
        end_t = time()
        print("Logit fitted in (%f s)" % (end_t-start_t))

        start_t = time()
        self.svm_fit = svm.LinearSVC().fit(samples, targets)
        end_t = time()
        print("SVM fitted in (%f s)" % (end_t-start_t))

        start_t = time()
        self.nb_fit = GaussianNB().fit(samples, targets)
        end_t = time()
        print("NB fitted in (%f s)" % (end_t-start_t))

        print("Training set size: %d" % len(samples))

    def parse_features(self, featuresfile, is_training):
        with open(featuresfile, 'r') as f:
            for line in f:
                vec = line.split("\t")
                word = vec[0] 
                sample = [float(vec[i]) for i in range(1, len(vec)-1)]
                if is_training:
                    target = int(vec[-1])
                    yield word, sample, target 
                else:
                    id = int(vec[-1])
                    yield word, sample, id 

    def next_sample(self, featurefile):
        cur_id = 0
        samples, words = [], []
        for word, vec, id in self.parse_features(featurefile, False):
            if id != cur_id:
                if cur_id != 0:
                    yield samples, words, cur_id 
                cur_id = id
                samples, words = [vec], [word]
            else:
                samples.append(vec)
                words.append(word)
        if cur_id != 0:
            yield samples, words, cur_id 

    def rank(self, samples, words):
        samples, preds = np.array(samples), []
        # no need to rank if 3 or less candidates
        if len(words) > 3:
            start_t = time()
            #samples = self.scaler.transform(samples)

            preds_lgt = self.logit_fit.decision_function(samples)
            preds_svm = self.svm_fit.decision_function(samples)
            #preds_nb = self.nb_fit.predict_proba(samples)
            #preds_nb = np.array([x[1] for x in preds_nb])

            preds = 0.7*preds_svm + 0.3*preds_lgt # + 0.05*preds_nb

            end_t = time()
            #print("Predictions made in (%f s)" % (end_t-start_t))

            #results = zip(words, preds_nb)
            #return [w for w, _ in sorted(results, key = lambda x: x[1][1], reverse=True)]

            results = zip(words, preds)
            return [w for w, _ in sorted(results, key = lambda x: x[1], reverse=True)]

        return words

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage: " + sys.argv[0] + " output.csv"
        sys.exit()

    #trainfeatures = sys.argv[1]
    #testfeatures = sys.argv[2]
    trainfeatures = 'data/features-train-13.5k.csv'
    testfeatures  = 'data/features-test-full.csv'
    #trainfeatures = 'data/scaledfeatures-train.csv'
    #testfeatures  = 'data/scaledfeatures-test.csv'
    resultsfile = sys.argv[1]

    tags = load_tags()
    selector = TagSelector(trainfeatures, tags)
    intersect = load_intersection('data/intersection.csv')
    correlated = load_correlated('data/correlated37.tags')

    count = 0
    for samples, words, idd in selector.next_sample(testfeatures):
        # ranked list of candidate tags
        finaltags = selector.rank(samples, words)
        # take top potential tags
        finaltags = finaltags[:3]
        ###### first choice ########
        better = list()
        for ftag in finaltags:
            lencor = len(correlated[ftag]) + 1 
            if lencor > 1:
                better = [ftag] + correlated[ftag]
                break
        # use better from correlated whenever possible
        if better:
            finaltags = better

        intersect[str(idd)] = '"' + ' '.join(finaltags) + '"'

        count += 1
        if count % 50000 == 0:
            print count

    out = open(resultsfile, 'w')
    out.write('Id,Tags\n')
    prev_id = 6034196
    for idd, tags in sorted(intersect.items()):
        idd = int(idd)
        dif = idd - prev_id
        for i in range(1, dif):
            out.write('{},"c# java php"\n'.format(prev_id+i, tags))
        out.write('{},{}\n'.format(idd, tags))
        prev_id = idd
    out.close()

