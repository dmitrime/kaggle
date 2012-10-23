#from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn import cross_validation
import numpy as np
from scipy import stats

def read_data(file_name):
    f = open(file_name)
    #ignore header
    cols = f.readline().split(",")
    cols = cols[1:]
    samples = []
    for line in f:
        line = line.strip().split(",")
        sample = [float(x) for x in line[1:]]
        samples.append(sample)
    f.close()
    return cols, samples

def write_delimited_file(file_path, data,header=None, delimiter=","):#{{{
    f_out = open(file_path,"w")
    if header is not None:
        f_out.write(delimiter.join(header) + "\n")
    for line in data:
        if isinstance(line, str):
            f_out.write(line + "\n")
        else:
            f_out.write(delimiter.join(line) + "\n")
    f_out.close()#}}}

def rsquared(answer, prediction):#{{{
    slope, intercept, r_value, p_value, std_err = stats.linregress(answer, prediction)
    return r_value*r_value#}}}

def filter_cols(train, cols, select):
    selected = []
    with open(select) as f:
        for line in f:
            selected.append(line.strip())
    colnums = []
    for s in selected:
        try:
            ind = cols.index(s)
            colnums.append(ind)
        except ValueError:
            pass
    newtrain = []
    for tr in train:
        newtrain.append([tr[c] for c in colnums])
    return newtrain

def main():
    for ind in range(1, 15+1):
    #for ind in [3,4,5,7,9,11,12,13,14,15]: # no 1,2,6,8,10
        print "TrainingSet/ACT%d_competition_training.csv" % ind
        #read in  data, parse into training and target sets
        cols, train = read_data("../TrainingSet/ACT%d_competition_training.csv" % ind)
        target = np.array( [x[0] for x in train] )

        train = filter_cols(train, cols, "../selected/selected_%d.txt" % ind)
        #print("Train: ", len(train), " cols:", len(train[0]))
        train = np.array( train )

        #In this case we'll use a random forest, but this could be any classifier
        cfr = ExtraTreesRegressor(n_estimators=1000, max_features=(len(train[0])//3), n_jobs=8, random_state=1279)

        #Simple K-Fold cross validation. 10 folds.
        cv = cross_validation.KFold(len(train), k=10, indices=False, shuffle=True)

        #iterate through the training and test cross validation segments and
        #run the classifier on each one, aggregating the results into a list
        results = []
        for traincv, testcv in cv:
            ft = cfr.fit(train[traincv], target[traincv])
            score = ft.score(train[testcv], target[testcv])
            results.append(score)
            print "\tFold %d: %f" % (len(results), score)

        #print out the mean of the cross-validated results
        print "Results: " + str( np.array(results).mean() )

if __name__=="__main__":
    main()
