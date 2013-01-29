#!/usr/bin/env python
from math import sqrt
from multiprocessing import Pool


def santa_input(fname):
    cities = []
    with open(fname) as f:
        header = f.readline()
        for line in f:
            k = line.split(',')
            cities.append( (int(k[0]), int(k[1]), int(k[2])) )
    print 'reading done!'
    return cities

def euclidean(p1, p2):
    return sqrt( (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2 )

def dist(cts):
    sum = 0.0
    for i in xrange(len(cts)-1):
        sum += euclidean(cts[i], cts[i+1])
    return sum

def mapper(params):
    start, segment, total, cts = params
    N = 25
    lbest = [[] for x in xrange(N)]
    for i in xrange(start, start+segment):
        dist = []
        for j in xrange(total):
            if i == j:
                continue
            d = euclidean(cts[i], cts[j])
            if len(dist) < N:
                dist.append( (d, j) )
            elif len(dist) == N:
                mxind = dist.index(max(dist))
                if d < dist[mxind][0]:
                    del dist[mxind]
                    dist.append( (d, j) )
        dist = sorted(dist)
        for x in xrange(N):
            lbest[x].append( (i, dist[x][1], dist[x][0]) )
    return lbest

def combiner(lists):
    fs = [open("best%d_dist.csv" % (x+1), "w") for x in xrange(len(lists[0]))]
    for sublist in lists:
        for i in xrange(len(sublist)):
            for b1 in sublist[i]:
                fs[i].write(",".join([ str(x) for x in b1 ]) + "\n")
    for i in xrange(len(sublist)):
        fs[i].close()

def compute_closest(cts):
    PROCS = 25
    def segments(procs):
        segments = []
        rem = len(cts)
        seglen = rem // procs
        start = 0
        for i in range(procs):
            segments.append( (start, seglen, rem, cts) )
            start += seglen
        return segments
    pool = Pool(processes=PROCS)
    lists = pool.map(mapper, segments(PROCS))
    return combiner(lists)

if __name__ == '__main__':
    cts = santa_input('santa_cities.csv')
    compute_closest(cts)

