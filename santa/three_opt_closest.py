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

def seq_swap(lsol2, pathnum, s1, e1, s2, e2):
    temp = []
    for i in xrange(s2, e2+1):
        temp.append(lsol2[i])
    for i in xrange(s1, e1+1):
        temp.append(lsol2[i])
    for i in xrange(s1, e2+1):
        lsol2[i] = temp[i-s1]
        pathnum[lsol2[i]] = i

def reconnect_path(lsol2, pathnum, typ, s1, e1, s2, e2, s3, e3):
    if typ == 1:
        reverse_segment(lsol2, pathnum, pathnum[e1], pathnum[s2])
        reverse_segment(lsol2, pathnum, pathnum[e2], pathnum[s3])
    elif typ == 2:
        seq_swap(lsol2, pathnum, pathnum[e1], pathnum[s2], pathnum[e2], pathnum[s3])
        reverse_segment(lsol2, pathnum, pathnum[e2], pathnum[s3])
        reverse_segment(lsol2, pathnum, pathnum[e1], pathnum[s2])
    elif typ == 3:
        seq_swap(lsol2, pathnum, pathnum[e1], pathnum[s2], pathnum[e2], pathnum[s3])
    elif typ == 4:
        seq_swap(lsol2, pathnum, pathnum[e1], pathnum[s2], pathnum[e2], pathnum[s3])
        reverse_segment(lsol2, pathnum, pathnum[e2], pathnum[s3])
    elif typ == 5:
        seq_swap(lsol2, pathnum, pathnum[e1], pathnum[s2], pathnum[e2], pathnum[s3])
        reverse_segment(lsol2, pathnum, pathnum[e1], pathnum[s2])
        
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

def compute_improvement(cts, sol1, rev1, start1, end1, start2, end2, start3, end3):
    results = []
    distsum = euclidean(cts[start1], cts[end1]) + euclidean(cts[start2], cts[end2]) + \
                          euclidean(cts[start3], cts[end3])
    # possible options of 3 new edges that reconnect the path
    combinations = [ [(start1, start2), (end1, start3), (end2, end3)], # option 1
                     [(start1, start3), (end2, start2), (end1, end3)], # option 2
                     [(start1, end2), (start3, end1), (start2, end3)], # option 3
                     [(start1, start3), (end2, end1), (start2, end3)], # option 4
                     [(start1, end2), (start3, start2), (end1, end3)]  # option 5
                   ]
    # find the shortest one
    for typ, comblist in enumerate(combinations):
        ndistsum = sum( [ euclidean(cts[begin], cts[end]) for begin, end in comblist ] )
        if distsum > ndistsum and all( [edge_unique(begin, end, sol1, rev1) for begin,end in comblist] ):
            results.append( (distsum-ndistsum, typ+1) )

    if len(results) > 0:
        results.sort()
        return results[-1]
    return (0,0)

def three_opt(sol1, rev1, sol2, cts):
    bests = load_bests()
    print 'bests loaded'

    lsol2, pathnum = path_to_list(sol2)
    impr, count = 0, 0
    imprstats = [0]*10
    for i in xrange(len(lsol2)-1):
        start1 = lsol2[i]
        end1   = lsol2[i+1]
        
        improve, best, imprtype = 0, 0, 0
        ind1, ind2, ind3, ind4, ind5, ind6 = 0, 0, 0, 0, 0, 0
        for c in xrange(len(bests)):
            start2 = bests[c][start1]
            pn = pathnum[start2]
            if pn+1 == len(lsol2):
                continue
            end2 = lsol2[pn+1]
            if end1 == start2 or end2 == start1:
                continue

            for d in xrange(len(bests)):
                start3 = bests[d][start1] 
                qn = pathnum[start3]
                if start3 == start2 or qn+1 == len(lsol2):
                    continue
                end3 = lsol2[qn+1]
                if end3 == start2 or end3 == start1 or end3 == end1 or end3 == end2:
                    continue

                pos = sorted([(i, start1, end1), (pathnum[start2], start2, end2), (pathnum[start3], start3, end3)])
                s1,e1,s2,e2,s3,e3 = pos[0][1], pos[0][2], pos[1][1], pos[1][2], pos[2][1], pos[2][2]
                improve, itype = compute_improvement(cts, sol1, rev1, s1, e1, s2, e2, s3, e3)

                if improve > best:
                    best = improve
                    ind1, ind2, ind3, ind4, ind5, ind6 = s1, e1, s2, e2, s3, e3
                    imprtype = itype

            for d in xrange(len(bests)):
                start3 = bests[d][start2] 
                qn = pathnum[start3]
                if start3 == start1 or qn+1 == len(lsol2):
                    continue
                end3 = lsol2[qn+1]
                if end3 == start2 or end3 == start1 or end3 == end1 or end3 == end2:
                    continue

                pos = sorted([(i, start1, end1), (pathnum[start2], start2, end2), (pathnum[start3], start3, end3)])
                s1,e1,s2,e2,s3,e3 = pos[0][1], pos[0][2], pos[1][1], pos[1][2], pos[2][1], pos[2][2]
                improve, itype = compute_improvement(cts, sol1, rev1, s1, e1, s2, e2, s3, e3)

                if improve > best:
                    best = improve
                    ind1, ind2, ind3, ind4, ind5, ind6 = s1, e1, s2, e2, s3, e3
                    imprtype = itype
                
        if best > 0:
            impr += best
            count += 1
            reconnect_path(lsol2, pathnum, imprtype, ind1, ind2, ind3, ind4, ind5, ind6)
            imprstats[imprtype] += 1

    sol2 = {}
    for i in xrange(len(lsol2)-1):
        sol2[ lsol2[i] ] = lsol2[i+1]
            
    print '3-opts made: ', count
    print 'type stats: ', imprstats
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

    return sol2

if __name__ == '__main__':
    cts = santa_input('santa_cities.csv')
    sol1, rev1, sol2, rev2 = read_solution('solutions/solution_2opt_both.csv')
    newsol2 = three_opt(sol1, rev1, sol2, cts)
    write_solutions('solution_3opt_final.csv', sol1, newsol2)
    

