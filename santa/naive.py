#!/usr/bin/env python
from math import sqrt

def write_tsp(fname, path):
    with open(fname, 'w') as f:
        f.write("\n".join([str(x) for x in path]))

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

def simple_tsp(cts):
    start, count, sum = 0, 1, 0
    path = [start]
    visited = [0]*len(cts)
    while count < len(cts):
        visited[start] = 1
        best, ind = 1000000, 0
        for i in xrange(len(cts)):
            if visited[i]:
                continue
            dist = euclidean(cts[start], cts[i])
            if dist < best:
                best, ind = dist, i
        sum += best
        start = ind
        path.append(ind)
        count += 1
        if count % 5000 == 0:
            print count
    return path, sum

if __name__ == '__main__':
    cts = santa_input('santa_cities.csv')
    path, sum = simple_tsp(cts)
    print 'sum: ', sum
    write_tsp('simple_tsp.csv', path)
