import networkx as nx

def get_given_optimal(G, pt):
    weightsum = 0
    for i in range(len(pt)-1):
        u = pt[i]
        v = pt[i+1]
        if u in G and v in G[u]:
            weightsum += G[u][v]['weight']
        else:
            return (len(pt), 1) # approximation, may be shorter
    return (weightsum, 0)

def get_current_optimal(G, pt):
    try:
        res = nx.bidirectional_dijkstra(G, pt[0], pt[-1])
        return (res[0], 0)
    except:
        return (1337, 1) # no path

if __name__ == '__main__':
    graphs = []
    nodes = 0
    for t in range(1, 15+1):
        G = nx.DiGraph()
        with open('../data/processed/train%d.txt' % t, 'r') as f:
            for line in f:
                parts = line.strip().split(' | ')
                u,v,wt = int(parts[0]), int(parts[1]), int(parts[2])
                G.add_edge(u, v, weight=wt)
                nodes = max(nodes, u, v)
        graphs.append(G)

    paths = []
    with open('../data/processed/paths.txt', 'r') as f:
        for line in f:
            parts = line.strip().split(' | ')
            paths.append( [int(node) for node in parts] )

    noGiven, noOptim, same, noPath, okPath, noBoth = 0, 0, 0, 0, 0, 0
    series = []
    for i, pt in enumerate(paths):
        optimal = []
        notfound = 0
        for G in graphs:
            opt, xgiven = get_given_optimal(G, pt)
            cur, xoptim = get_current_optimal(G, pt)

            noGiven += xgiven
            noOptim += xoptim
            if xgiven == xoptim == 1:
                noPath += 1
            if xgiven == xoptim == 0:
                okPath += 1
            if cur == opt: 
                same += 1

            # both paths do not exist
            if xgiven == xoptim == 1: 
                notfound += 1

            optimal.append(1.0 if cur == opt else 0.0)

        if notfound == len(graphs):
            noBoth += 1
            #print pt
            
        series.append(optimal)

    print "mapping contains %d nodes\n" % (nodes+1)
    print "150000 paths in 15 graphs:" 
    print "\t%d given optimal paths could not be followed" % noGiven
    print "\t%d current optimal paths could not be followed" % noOptim
    print "\t%d given and current paths were the same" % same
    print "\t%d paths both didn't exist" % noPath
    print "\t%d paths both existed" % okPath
    print "\t%d no paths existed in any of the graphs" % noBoth

    predictions = []
    for sr in series:
        predictions.append( str(sum(sr) / 15.0) )

    submission = ["Prediction"]
    for i in range(5):
        submission.extend(predictions)

    g = open("submission2-mode-Nov20.csv", 'w')
    g.write("%s" % "\n".join(submission))
    g.close()

