from collections import defaultdict

if __name__ == '__main__':
    trainfile = 'data/TrainProc.csv'

    corr = dict()
    ocur = defaultdict(int)
    with open(trainfile, 'r') as f:
        #skip first
        f.readline()
        for line in f:
            parts = line.lower().strip(' ').strip('\n').strip('"').split('","', 2)
            if len(parts) < 3: continue
            id, title, rest = parts
            comma = rest.rfind(',')
            body, giventags = rest[:comma-1], rest[comma+2:].split()

            for tag in giventags:
                ocur[tag] += 1
                if tag not in corr:
                    corr[tag] = defaultdict(int)
                for t in giventags:
                    if tag != t:
                        corr[tag][t] += 1

    g = open('data/correlated37.tags', 'w')
    for tag, simtags in corr.items():
        tagocur = float(ocur[tag])

        correlated = list()
        for stag, socur in simtags.items():
            ratio = float(socur) / tagocur
            if ratio >= 0.37:
                correlated.append(stag)

        if correlated:
            g.write('{} {}\n'.format(tag, ','.join(correlated)))
    g.close()

