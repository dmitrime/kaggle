from sklearn.ensemble import RandomForestRegressor
from sklearn import cross_validation
import numpy as np
from scipy import stats

def read_data(file_name):
    f = open(file_name)
    cols = f.readline().split(",")
    cols = cols[1:]
    rows, samples = [], []
    for line in f:
        line = line.strip().split(",")
        sample = [float(x) for x in line[1:]]
        rows.append(line[0])
        samples.append(sample)
    f.close()
    return cols, rows, samples

def write_file(file_path, colnames, colpreds, delimiter=","):#{{{
    f_out = open(file_path,"w")
    for ind in range(len(colnames)):
        f_out.write("\"" + colnames[ind] + "\"" + delimiter + str(colpreds[ind]) + "\n")
    f_out.close()#}}}

def rsquared(answer, prediction):#{{{
    slope, intercept, r_value, p_value, std_err = stats.linregress(answer, prediction)
    return r_value*r_value#}}}

def filter_cols(dset, cols, select):
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
    newset = []
    for row in dset:
        newset.append([row[c] for c in colnums])
    return newset

def main():
    for ind in range(1, 15+1):
        print "TrainingSet/ACT%d_competition_training.csv" % ind
        #read in  data, parse into training and target sets
        cols, _, train = read_data("../TrainingSet/ACT%d_competition_training.csv" % ind)
        target = np.array( [x[0] for x in train] )

        train = filter_cols(train, cols, "../selected/selected_%d.txt" % ind)
        train = np.array(train)
        #print("Train: ", len(train), " cols:", len(train[0]))

        #In this case we'll use a random forest, but this could be any classifier
        cfr = RandomForestRegressor(n_estimators=500, max_features=(len(train[0])//3), n_jobs=8)
        rf = cfr.fit(train, target)

        cols, molecules, test = read_data("../TestSet/ACT%d_competition_test.csv" % ind)
        test = filter_cols(test, cols, "../selected/selected_%d.txt" % ind)
        test = np.array(test)

        pred = rf.predict(test)
        write_file("submissions/rf_submission_%d.csv" % ind, molecules, pred)

if __name__=="__main__":
    main()
