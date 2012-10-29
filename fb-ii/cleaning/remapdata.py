if __name__ == '__main__':
    m = {}
    with open('mapping-full.txt', 'r') as f:
        for line in f:
            s, n = line.strip().split(' | ')
            m[s] = n

    for t in range(1, 15+1):
        g = open("../data/processed/train%d.txt" % t, 'w')
        with open('../data/train%d.txt' % t, 'r') as f:
            for line in f:
                parts = line.strip().split(' | ')
                g.write("%s\n" % ' | '.join([m[parts[0]], m[parts[1]], parts[2]]) )
        g.close()

    g = open("../data/processed/paths.txt", 'w')
    with open('../data/paths.txt', 'r') as f:
        for line in f:
            parts = line.strip().split(' | ')
            newparts = [ m[part] for part in parts ]
            g.write("%s\n" % ' | '.join(newparts))
    g.close()

