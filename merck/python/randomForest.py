from sklearn.ensemble import RandomForestRegressor
from sklearn import cross_validation
import numpy as np
from scipy import stats

def read_data(file_name, off):
    f = open(file_name)
    #ignore header
    cols = f.readline().split(",")
    cols = cols[off:]
    samples = []
    for line in f:
        line = line.strip().split(",")
        sample = [float(x) for x in line[off:]]
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
    #read in  data, parse into training and target sets
    cols, train = read_data("../TrainingSet/ACT12_competition_training.csv", 1)
    target = np.array( [x[0] for x in train] )

    train = filter_cols(train, cols, "../selected/selected_12.txt")
    #print("Train: ", len(train), " cols:", len(train[0]))
    train = np.array( train )

    #In this case we'll use a random forest, but this could be any classifier
    cfr = RandomForestRegressor(n_estimators=500, max_features=(len(train[0])//3), n_jobs=8)

    #Simple K-Fold cross validation. 10 folds.
    cv = cross_validation.KFold(len(train), k=5, indices=False)

    #iterate through the training and test cross validation segments and
    #run the classifier on each one, aggregating the results into a list
    results = []
    for traincv, testcv in cv:
        ft = cfr.fit(train[traincv], target[traincv])
        pred = ft.predict(train[traincv])
        print pred[:10]
        score = ft.score(train[traincv], target[traincv])
        results.append(score)
        print "\tFold %d: %f" % (len(results), score)

    #print out the mean of the cross-validated results
    print "Results: " + str( np.array(results).mean() )

if __name__=="__main__":
    main()
