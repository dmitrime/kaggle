#!/usr/bin/env python
from math import sqrt

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
    li1, li2 = [0], [0]

    start = 0
    while start in sol1: 
        nxt = sol1[start]
        li1.append(nxt)
        start = nxt
    start = 0
    while start in sol2: 
        nxt = sol2[start]
        li2.append(nxt)
        start = nxt

    for i in xrange(len(li1)):
        f.write(str(li1[i]) + ',' + str(li2[i]) + '\n')
    f.close()

def read_solution(fname):
    path1, path2 = {}, {}
    rev1, rev2 = {}, {}
    with open(fname) as f:
        k = f.readline().split(',')
        s1, s2 = int(k[0]), int(k[1])
        for line in f:
            k = line.split(',')
            e1, e2 = int(k[0]), int(k[1])
            path1[s1], path2[s2] = e1, e2
            rev1[e1], rev2[e2] = s1, s2
            s1, s2 = e1, e2
    return path1, rev1, path2, rev2

def euclidean(p1, p2):
    return sqrt( (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2 )

def edge_unique(begin, end, prev, rprev):
    return (end not in prev or prev[end] != begin) \
       and (begin not in rprev or rprev[begin] != end) \
       and (end not in rprev or rprev[end] != begin) \
       and (begin not in prev or prev[begin] != end)

def check_edges(sol1, cts, start):
    sum, count = 0, 0
    while start in sol1:
        sum += euclidean(cts[start], cts[ sol1[start] ])
        start = sol1[start]
        count += 1
    return count, sum

# ... - S1 - E1 - ... - S2 - E2 - ...
# becomes
# ... - S1 - REV(S2,E1) - E2 - ...
def reverse_segment(lsol2, pathnum, begin, end):
    for i in xrange(begin, begin + (end-begin) // 2 + 1):
        rev = end - (i-begin)
        pathnum[ lsol2[i] ], pathnum[ lsol2[rev] ] = rev, i
        lsol2[i], lsol2[rev] = lsol2[rev], lsol2[i]
    
def load_bests():
    bests = []
    for i in range(1,25+1):
        with open("bests/best%d_dist.csv" % i) as f:
            best = {}
            for line in f:
                k = line.split(',')
                best[ int(k[0]) ] = int(k[1])
        bests.append(best)
    return bests

def path_to_list(sol2):
    lsol2, pathnum = [], {}
    start, c = 0, 0
    while start in sol2:
        lsol2.append(start)
        pathnum[start] = c
        c += 1
        start = sol2[start]
    lsol2.append(start)
    pathnum[start] = c
    return lsol2, pathnum

def two_opt(sol1, rev1, sol2, cts):
    bests = load_bests()
    print 'bests loaded'

    lsol2, pathnum = path_to_list(sol2)
    impr, count = 0, 0
    for i in xrange(len(lsol2)-1):
        start1 = lsol2[i]
        end1   = lsol2[i+1]
        
        improve, best = 0, 0
        ind1, ind2 = 0, 0
        for c in xrange(len(bests)):
            start2 = bests[c][start1]
            pn = pathnum[start2]
            if pn+1 == len(lsol2):
                break
            end2 = lsol2[pn+1]
            
            if end1 == start2 or end2 == start1:
                continue

            dist1, dist2 = euclidean(cts[start1], cts[end1]), euclidean(cts[start2], cts[end2])
            ndist1, ndist2 = euclidean(cts[start1], cts[start2]), euclidean(cts[end1], cts[end2])
            if dist1+dist2 > ndist1+ndist2:
                improve = (dist1+dist2) - (ndist1+ndist2)
                                 #and i < pn \
                if improve > best and edge_unique(start1, start2, sol1, rev1) \
                                  and edge_unique(end1, end2, sol1, rev1):
                    best = improve
                    ind1, ind2 = start2, end2
        if best > 0:
            impr += best
            count += 1
            if i > pathnum[ind1]:
                reverse_segment(lsol2, pathnum, pathnum[ind1]+1, i)
            else:
                reverse_segment(lsol2, pathnum, i+1, pathnum[ind1])

    sol2 = {}
    for i in xrange(len(lsol2)-1):
        sol2[ lsol2[i] ] = lsol2[i+1]
    rev2 = {}
    for i in xrange(len(lsol2)-1, 0, -1):
        rev2[ lsol2[i] ] = lsol2[i-1]
            
    print '2-opts made: ', count
    print 'improvement: ', impr
    print 'Check path2: ', check_edges(sol2, cts, 0)

    c1, c2 = 0,0
    for k,v in sol1.items():
        if (k in sol2 and sol2[k] == v):
            print 'Edge: %d -> %d' % (k,v)
            c1 += 1
    for k,v in rev1.items():
        if (k in sol2 and sol2[k] == v):
            print 'REdge: %d -> %d' % (k,v)
            c2 += 1
    print c1,c2

    return sol2, rev2

if __name__ == '__main__':
    cts = santa_input('santa_cities.csv')
    sol1, rev1, sol2, rev2 = read_solution('solutions/solution_greedy_simple_tsp.csv')
    newsol1, newrev1 = two_opt({}, {}, sol1, cts)
    newsol2, newrev2 = two_opt(newsol1, newrev1, sol2, cts)
    write_solutions('solution_2opt_both.csv', newsol1, newsol2)
    

