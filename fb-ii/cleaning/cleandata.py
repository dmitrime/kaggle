from collections import defaultdict
from hashes.simhash import simhash
import re
import random
from disjointset import DisjointSet
from multiprocessing import Pool

# Hashbits
HB = 64
# Number of processors
PROC = 18

def process(s):
    tok = re.sub('^--?', '', s)
    tok = re.sub(' - -?', ' ', tok)
    tok = re.sub('\s?&\s?', '-and-', tok)
    tok = re.sub('[?.!,;:@+&#/]', '', tok)
    tok = re.sub('^-', '', tok)
    tok = re.sub(' -$', '', tok)
    return tok.strip().lower()

def count_matches(words1, words2):
    exact, subs, bags = 0,0,0
    for w1 in words1:
        f1, f2, f3 = True, True, True
        for w2 in words2:
            if f1 and w1 == w2:
                exact += 1
                f1 = False
            if f2 and w1.find(w2) != -1 or w2.find(w1) != -1:
                subs += 1
                f2 = False
            if f3 and sorted(list(w1)) == sorted(list(w2)):
                bags += 1
                f3 = False
    return (exact, subs, bags)

def strings_remaining(strings, ds):
    rem = {}
    for i in xrange(len(strings)):
        p1,p2 = strings[i]
        node = ds.find(p2)
        rem[node.data] = node.key
    return [(k,v) for k,v in rem.items()]

def mapper(params):#{{{
    start1, start2, segment, total, hashes, dglinks = params
    merging = []
    #f = open("links/dglinks-%d.txt" % random.randint(0, 10000), 'w')
    for start in [start1, start2]:
        for i in xrange(start, start+segment):
            hash1 = hashes[i]
            for j in xrange(i+1, total):
                hash2 = hashes[j]
                sim = hash1.similarity(hash2)
                if sim >= 0.85: 
                    merging.append( (i,j) )
                if (sim >= 0.825 and dglinks[i].intersection(dglinks[j]) != set([]) ):
                    merging.append( (i,j) )
                    #f.write("%s\n%s\n\n" % (remain[i], remain[j]))
    #f.close()
    return merging

def combiner(lists):
    combined = []
    for sublist in lists:
        for pair in sublist:
            combined.append(pair)
    return combined

def find_merges_by_hash(remaining, hashes, dglinks):

    def get_segments(p):
        segments = []
        rml = len(remaining)
        # each process gets a segment from the head and tail of the list
        seglen = rml // (2*p) 
        start = 0
        for i in range(p):
            segments.append( (start, rml-start-seglen, seglen, rml, hashes, dglinks) )
            start += seglen
        return segments

    pool = Pool(processes=PROC) 
    lists = pool.map(mapper, get_segments(PROC))
    return combiner(lists)#}}}

def merge_sets(ds, remaining, mergelist):
    keywords = set(['inc', 'llc', 'co', 'ltd', 'srl', 'as', 'sa', 'computer', 'network', 'system', 'systems', 'telecom', 'internet', 'corp', 'corporation', 'net', 'com', 'company'])
    g = open("merge-list.txt", 'w')
    counter = 0
    for i,j in mergelist:
        p1,p2 = remaining[i]
        q1,q2 = remaining[j]

        k1, k2 = p1.split(), q1.split()
        k1, k2 = list( set(k1).difference(keywords) ), list( set(k2).difference(keywords) )
        ex, sb, bg = count_matches(k1, k2)
        lk1, lk2 = len(k1), len(k2)

        cond1 = len(p1) == len(q1) and sorted(list(p1)) == sorted(list(q1))
        cond2 = abs(len(p1)-len(q1)) == 1 and set(p1).difference('-') == set(q1).difference('-')
        cond3 = (lk1 == 3 or lk2 == 3) and ex == 2
        cond4 = ex >= 3 
        cond5 = ex >= 1 and (ex == lk1 or ex == lk2)
        cond6 = lk1 > 2 and lk2 > 2 and bg >= min(lk1, lk2)-1

        if cond1 or cond2 or cond3 or cond4 or cond5 or cond6:
            ds.union(p2, q2)
            g.write("%s\n%s\n\n" % (p1, q1))
        else:
            g.write("SKIPPED\n%s\n%s\n\n" % (p1, q1))
            counter += 1
    g.close()
    print "indices skipped: %d" % counter

def write_mapping(digits, ds, strings, N):#{{{
    strmap = {}
    g1 = open("mapping-processed.txt", 'w')
    g2 = open("mapping-full.txt", 'w')

    for name, num in digits.items():
        g1.write("%s | %d\n" % (name, num))
        g2.write("%s | %d\n" % (name, num))

    for i in xrange(len(strings)):
        proc, orig = strings[i]
        node = ds.find(orig)
        if not node.key in strmap:
            strmap[ node.key ] = N
            N += 1
        g1.write("%s | %d\n" % (proc, strmap[node.key]))
        g2.write("%s | %d\n" % (orig, strmap[node.key]))

    g1.close()
    g2.close()
    print "digit nodes: %d" % len(digits)
    print "text nodes: %d" % len(strmap)
    print "total nodes: %d" % (len(strmap) + len(digits))#}}}

if __name__ == '__main__':
    N = 0
    digits = {}
    digit_in, digit_out = defaultdict(list), defaultdict(list)
    strings = []
    ds = DisjointSet()
    for t in range(1, 15+1):
        with open('../data/train%d.txt' % t, 'r') as f:
            for line in f:
                parts = line.strip().split(' | ')
                part1, part2 = parts[0], parts[1]
                proc1, proc2 = process(part1), process(part2)
                # part 1
                if part1.isdigit():
                    if part1 not in digits:
                        digits[part1] = N
                        N += 1
                    if not part2.isdigit():
                        digit_out[proc2].append(part1)
                else:
                    strings.append( (proc1, part1) )
                    ds.makeSet(part1, proc1)
                # part 2
                if part2.isdigit():
                    if part2 not in digits:
                        digits[part2] = N
                        N += 1
                    if not part1.isdigit():
                        digit_in[proc1].append(part2)
                else:
                    strings.append( (proc2, part2) )
                    ds.makeSet(part2, proc2)

    with open('../data/paths.txt', 'r') as f:
        for line in f:
            parts = line.strip().split(' | ')
            for part in parts:
                if part.isdigit():
                    if part not in digits:
                        digits[part] = N
                        N += 1
# TODO: add to digit_in, digit_out
                else:
                    strings.append( (process(part), part) )
                    ds.makeSet(part, process(part))

    # sort the strings and do a linear scan merging the neighbours along the way
    strings = sorted(strings)
    g = open("merged-linear.txt", 'w')
    for i in xrange(1, len(strings)):
        p1,p2 = strings[i]
        q1,q2 = strings[i-1]
        if p1 == q1:
            ds.union(p2, q2)
        elif ds.find(p2) != ds.find(q2):
            k1, k2 = p1.split(), q1.split()

            w1, w2 = k1[0], k2[0]
            equal = w1 == w2
            exact, subs, bags = count_matches(k1[1:], k2[1:])
            lenOk = len(w1) > 2 and len(w2) > 2

            cond1 = exact > 1 and lenOk  and (w1 == w2 or w1.find(w2) != -1 or w2.find(w1) != -1)
            cond2 = w1 == w2 and lenOk and len(k2) == 1 and len(k1) == 2
            cond3 = exact >= 2 and len(k2) == 3 and len(k1) == 3
            cond4 = w1 == w2 and lenOk and ((bags == 1 and len(k1)+len(k2) <= 5) or (bags == 2 and len(k1)+len(k2) <= 7))

            if cond1 or cond2 or cond3 or cond4:
                ds.union(p2, q2)
                g.write("%s\n%s\n\n" % (p1, q1))
    g.close()

    remaining = strings_remaining(strings, ds)
    print 'merged neighbours, remaining: %d' % len(remaining)

    hashes, dglinks = [], []
    for k,v in remaining:
        hashes.append(simhash(k, hashbits=HB))
        dglinks.append(set(digit_in[k]).union(set(digit_out[k])))
    print 'hashing done'

    merging = find_merges_by_hash(remaining, hashes, dglinks)
    print "indices found: %d" % len(merging)
    merge_sets(ds, remaining, merging)
    print 'merged by hashes'

    write_mapping(digits, ds, strings, N)
    print 'done'

