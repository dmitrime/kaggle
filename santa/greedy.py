#!/usr/bin/env python
from math import sqrt
from two_opt_closest import *

START1 = 0
START2 = 0

def santa_input(fname):
    cities = []
    with open(fname) as f:
        header = f.readline()
        for line in f:
            k = line.split(',')
            cities.append( (int(k[0]), int(k[1]), int(k[2])) )
    return cities

def write_solutions(fname, sol1, sol2):
    f = open(fname, 'w')
    li1, li2 = [START1], [START2]

    start = START1
    while start in sol1: 
        nxt = sol1[start]
        li1.append(nxt)
        start = nxt
    start = START2
    while start in sol2: 
        nxt = sol2[start]
        li2.append(nxt)
        start = nxt

    for i in xrange(len(li1)):
        f.write(str(li1[i]) + ',' + str(li2[i]) + '\n')
    f.close()

def euclidean(p1, p2):
    return sqrt( (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2 )

def check_edges(sol1, cts, start):
    sum, count = 0, 0
    while start in sol1:
        sum += euclidean(cts[start], cts[ sol1[start] ])
        start = sol1[start]
        count += 1
    return count, sum

def edge_unique(begin, end, prev, rprev):
    return (end not in prev or prev[end] != begin) \
       and (begin not in rprev or rprev[begin] != end) \
       and (end not in rprev or rprev[end] != begin) \
       and (begin not in prev or prev[begin] != end)

def merge_segments(sol1, rev1, sum, segments, prev, rprev):
    print 'merging...'
    start, end = segments[0]
    del segments[0]
    while len(segments):
        best, ind = 100000000, -1
        for i in xrange(len(segments)):
            begin, finish = segments[i]
            d = euclidean(cts[end], cts[begin])
            if d < best and edge_unique(begin, end, prev, rprev):
                best, ind = d, i

        sum += best
        sol1[end] = segments[ind][0]
        rev1[segments[ind][0]] = end
        end = segments[ind][1]
        del segments[ind]
    return sum

def make_segments(sol1, rev1, lcts, bests, start, prev, rprev):
    segments = []
    visited = [False]*lcts
    cur, ind, sum = start, 0, 0
    cnt = 0
    while True:
        increment = True
        # visit this city
        visited[cur] = True
        # search for the next closest city
        for i in range(len(bests)):
            nxt, ln = bests[i][cur]
            if not visited[nxt] and edge_unique(cur, nxt, prev, rprev):
                cnt += 1
                break
        else:
            # closest not found, add to dangling for further processing
            segments.append( (start, cur) )
            # find next unvisited city
            while ind < lcts and visited[ind]:
                ind += 1
            # all visited, stop
            if ind >= lcts:
                break
            # make unvisited city the new current
            cur, start = ind, ind
            increment = False

        if increment:
            sum += ln
            sol1[cur] = nxt
            rev1[nxt] = cur
            cur = nxt
    print 'visited: ', len(visited)
    return segments, sum

def greedy(sol1, rev1, cts):
    bests = []
    for i in range(1,25+1):
        with open("bests/best%d_dist.csv" % i) as f:
            best = {}
            for line in f:
                k = line.split(',')
                best[ int(k[0]) ] = (int(k[1]), float(k[2]))
        bests.append(best)

    sol2, rev2 = {}, {}
    segments2, sum2 = make_segments(sol2, rev2, len(cts), bests, START2, sol1, rev1)
    print 'Segments2: ', len(segments2)

    sum2 = merge_segments(sol2, rev2, sum2, segments2, sol1, rev1)
    print 'Sum2: ', sum2
    print 'Check2: ', check_edges(sol2, cts, START2)

    # Check that we have no similar edges in the two paths
    c1, c2 = 0,0
    for k,v in sol1.items():
        if (k in sol2 and sol2[k] == v):
            print 'Edge: %d -> %d' % (k,v)
            c1 += 1
        if (v in rev2 and rev2[v] == k):
            print 'Reverse edge: %d <- %d' % (k,v)
            c1 += 1
    for k,v in rev1.items():
        if (k in sol2 and sol2[k] == v):
            print 'REdge: %d -> %d' % (k,v)
            c2 += 1
        if (v in rev2 and rev2[v] == k):
            print 'RReverse edge: %d <- %d' % (k,v)
            c2 += 1
    print c1,c2

    return sol2

def read_solution1(fname):
    sol1, rev1 = {}, {}
    reverse = []
    with open(fname) as f:
        k = f.readline().split()
        prev = int(k[0])
        reverse.insert(0, prev)
        for line in f:
            k = line.split()
            cur = int(k[0])
            sol1[prev] = cur
            reverse.insert(0, cur)
            prev = cur
    for i in xrange(len(reverse)-1):
        rev1[ reverse[i] ] = reverse[i+1]
    print len(sol1), len(rev1)
    return sol1, rev1

if __name__ == '__main__':
    cts = santa_input('santa_cities.csv')

    sol1, rev1 = read_solution1('solutions/simple_tsp.csv')
    sol1, rev1 = two_opt({}, {}, sol1, cts)

    sol2 = greedy(sol1, rev1, cts)
    sol2, rev2 = two_opt(sol1, rev1, sol2, cts)

    write_solutions('solution_2opt_both.csv', sol1, sol2)

