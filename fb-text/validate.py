import sys
import random
import string
import re
from collections import defaultdict
from predictor import TagSelector, TagBagger
from commons import *

class Quality:
    def __init__(self):
        self.count = 0
        self.f1 = 0.0
        self.precision = 0.0
        self.recall = 0.0

    def evaluate(self, tagset, predset, quiet=False):
        tp = len(tagset.intersection(predset))
        fp = len(predset.difference(tagset)) 
        fn = len(tagset.difference(predset))

        p = 1.0*tp / (tp + fp) if tp+fp > 0 else 0.0
        r = 1.0*tp / (tp + fn) if tp+fn > 0 else 0.0
        f = 2*p*r / (p+r)     if p+r > 0 else 0.0

        self.f1 += f
        self.precision += p
        self.recall += r
        self.count += 1

        if not quiet:
            print 'tagset: ', tagset
            print 'prdset: ', predset
            print 'f1 = ', f, 'prec  = ', p, ', rec = ',r
            print

    def report(self):
        print "Mean F1 %f" % (self.f1 / self.count)
        print "Mean Prec %f" % (self.precision / self.count)
        print "Mean Recall %f" % (self.recall / self.count)
        print


def report_quality(validation, preds):
    qual = Quality()
    for idd,  _, _, tagset in read_train_data(validation):
        predset = set(preds[idd])
        qual.evaluate(tagset, predset, True)
    qual.report()


if __name__ == '__main__2':
    validation = 'data/LightValidationProc.csv'
    clusters = 'data/clusterbag-tag.csv'

    stops = load_stops()
    bagger = TagBagger(clusters)

    print 'Predicting...'
    preds = defaultdict(str)
    count = 0
    for idd, title, body, _ in read_train_data(validation):
        finaltags = bagger.rank(set(bag_words(title, body, stops)))
        preds[str(idd)] = finaltags
        count += 1
        if count % 1000 == 0:
            print count

    print 'Done'

    report_quality(validation, preds)

if __name__ == '__main__':
    validation = 'data/LightValidationProc.csv'
    trainfeatures = 'data/features-train-6.7k.csv'
    testfeatures  = 'data/features-test-light.csv'
    clusters = 'data/clusterbag-tag.csv'

    selector = TagSelector(trainfeatures, load_tags())
    correlated = load_correlated('data/correlated37.tags')

    print 'Predicting...'
    c1, c2 = 0, 0
    missed = set()
    preds = defaultdict(str)
    for samples, words, idd in selector.next_sample(testfeatures):
        finaltags = selector.rank(samples, words)
        finaltags = finaltags[:3]

        ###### longest choice ########
        #better = list()
        #for ftag in finaltags:
            #lencor = len(correlated[ftag]) + 1 
            #if lencor > 1 and len(better) > lencor:
                #better = [ftag] + correlated[ftag]
        #if better:
            #finaltags = better
        ###### shortest choice ########
        #better, bmax = list(), 6
        #for ftag in finaltags:
            #lencor = len(correlated[ftag]) + 1 
            #if lencor > 1 and bmax > lencor:
                #better = [ftag] + correlated[ftag]
                #bmax = len(better)
        ###### first choice ########
        better = list()
        for ftag in finaltags:
            lencor = len(correlated[ftag]) + 1 
            if lencor > 1:
                better = [ftag] + correlated[ftag]
                break
        # use better from correlated whenever possible
        if better:
            finaltags = better #[:5]
            c1 += 1
        else:
            c2 += 1
            missed.add(str(idd))

        preds[str(idd)] = finaltags
    print 'Done'
    print '{} better, {} ranked'.format(c1, c2)

    do_missed = True
    if do_missed:
        print 'Predicting missed...'
        bagger = TagBagger(clusters)
        stops = load_stops()
        count = 0
        for idd, title, body, _ in read_train_data(validation):
            if idd in missed:
                finaltags = bagger.rank(set(bag_words(title, body, stops)))
                if set(finaltags).intersection(preds[str(idd)]):
                    preds[str(idd)] = list(set(finaltags).union(preds[str(idd)]))[:5]
                count += 1
                if count % 1000 == 0:
                    print count
        print 'Done'

    report_quality(validation, preds)

