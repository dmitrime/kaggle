import sys
import random
from commons import *

def random_words(bag, limit):
    return set(random.sample(bag, limit))

def tag_words(bag, tags, alltags):
    return set(tags).union(set(filter(lambda w: w in alltags, list(bag))))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage: " + sys.argv[0] + " training.csv"
        sys.exit()

    inputfile = sys.argv[1]
    tag_idset, id_tagset = dict(), dict()
    for idd, title, body, giventags in read_train_data(inputfile):
        if len(giventags) >= 3:
            tupletags = tuple(giventags)
            if tupletags not in tag_idset:
                tag_idset[tupletags] = set()
            tag_idset[tupletags].add(idd)
            #id_tagset[idd] = giventags

    MIN_IDS, MAX_IDS = 25, 50
    id_wordbag = dict()
    clusters = 0
    with open('data/clusters.csv', 'w') as g:
        # not a perfect clustering algorithm, but good enough for our purpose
        for tags, ids in tag_idset.items():
            if len(ids) >= MIN_IDS:
                docs = list(ids)[:MAX_IDS]
                for d in docs:
                    id_wordbag[d] = set()
                g.write('{}\t{}\n'.format(','.join(tags), ','.join(docs)))
                clusters += 1
    print clusters

    stops = load_stops()
    alltags = load_tags()
    for idd, title, body, giventags in read_train_data(inputfile):
        if idd not in id_wordbag: continue
        id_wordbag[idd] = bag_words(title, body, stops)

    with open('data/clusterbag-tag.csv', 'w') as g:
        # not a perfect clustering algorithm, but good enough for our purpose
        for tags, ids in tag_idset.items():
            if len(ids) >= MIN_IDS:
                docs = list(ids)[:MAX_IDS]
                bag = set()
                for d in docs:
                    bag.update(id_wordbag[d])
                #bag = random_words(bag, 100)
                bag = tag_words(bag, tags, alltags)
                g.write('{}\t{}\n'.format(','.join(tags), ','.join(list(bag))))

