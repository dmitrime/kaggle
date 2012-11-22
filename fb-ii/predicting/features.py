import networkx as nx
from random import randint
from multiprocessing import Pool

NOPATH = 99

def get_given_optimal(G, pt):
    weightsum = 0
    for i in range(len(pt)-1):
        u = pt[i]
        v = pt[i+1]
        if u in G and v in G[u]:
            weightsum += G[u][v]['weight']
        else:
            return (len(pt), False) # approximation, may be shorter
    return (weightsum, True)

def get_current_optimal(G, pt):
    try:
        res = nx.bidirectional_dijkstra(G, pt[0], pt[-1])
        return (res[0], True)
    except:
        return (NOPATH, False) # no path

def generate_path(G, nodes):
    while True:
        points = randint(0, nodes),randint(0, nodes)
        res = get_current_optimal(G, points)
        if res[1]:
            return ((points[0], points[1]), res[0])

def parallelize_training():
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

    # generate paths from the first 10 graphs
    paths = []
    for t in range(10):
        for x in range(1000):
            paths.append(generate_path(graphs[t], nodes))

    def get_params(graphs, paths):
        return [(g, graphs, paths) for g in range(10, 15)]

    pool = Pool(processes=5) 
    lists = pool.map(mapper, get_params(graphs, paths))

def mapper(params):
    g, graphs, paths = params
    f = open("parallel/train-features-%d.txt" % (g+1-10), 'w')
    header = "\t".join(["g%d" % i for i in range(1,11)]) + "\topt\tlastOpt\tchanges\tnopath\ty\n"
    f.write(header) 
    for pt, opt in paths:
        vec = []
        changes, nopath = 0, 0
        last = 0
        for x in range(10):
            res, isOk = get_current_optimal(graphs[x], pt)
            vec.append( str(res) )
            if res != opt:
                changes += 1
            if isOk == False:
                nopath += 1
            if x == 9 and res == opt:
                last = 1

        res = get_current_optimal(graphs[g], pt)
        vec.append( str(opt) )
        vec.append( str(last) )
        vec.append( str(changes) )
        vec.append( str(nopath) )
        vec.append( '1' if res[0] == opt else '0' )
        f.write( "\t".join(vec) + "\n")
    f.close()

def build_training():#{{{
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

    # generate paths from the first 10 graphs
    paths = []
    for t in range(10):
        for x in range(1000):
            paths.append(generate_path(graphs[t], nodes))

    for g in range(10, 15):
        f = open("train-features-%d.txt" % (g+1-10), 'w')
        header = "\t".join(["g%d" % i for i in range(1,11)]) + "\topt\tchanges\tnopath\ty\n"
        f.write(header) 
        for pt, opt in paths:
            vec = []
            changes, nopath = 0, 0
            for x in range(10):
                res, isOk = get_current_optimal(graphs[x], pt)
                vec.append( str(res) )
                if res != opt:
                    changes += 1
                if isOk == False:
                    nopath += 1

            res = get_current_optimal(graphs[g], pt)
            vec.append( str(opt) )
            vec.append( str(changes) )
            vec.append( str(nopath) )
            vec.append( '1' if res[0] == opt else '0' )
            f.write( "\t".join(vec) + "\n")
        f.close()#}}}

def build_test():
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

    files = []
    for g in range(5):
        f = open("parallel/test-features-%d.txt" % (g+1), 'w')
        header = "\t".join(["g%d" % i for i in range(1,11)]) + "\topt\tlastOpt\tchanges\tnopath\n"
        f.write(header) 
        files.append(f)

    npcount = 0
    for pt in paths:
        opt = NOPATH
        for z in range(15):
            opt2, isOk = get_given_optimal(graphs[z], pt)
            if isOk:
                opt = min(opt, opt2)
        if opt == NOPATH:
            opt = len(pt)
            npcount += 1

        vec = []
        last = 0
        changes, nopath = 0, 0
        for x in range(5, 15):
            res, isOK = get_current_optimal(graphs[x], pt)
            vec.append( str(res) )
            if res != opt:
                changes += 1
            if res == NOPATH:
                nopath += 1
            if x == 14 and res == opt:
                last = 1

        vec.append( str(opt) )
        vec.append( str(last) )
        vec.append( str(changes) )
        vec.append( str(nopath) )
        for f in files:
            f.write( "\t".join(vec) + "\n" )

    for f in files:
        f.close()
    print "Test paths with no optimum: %d" % npcount

if __name__ == '__main__':
    #build_training()
    parallelize_training()
    build_test()

