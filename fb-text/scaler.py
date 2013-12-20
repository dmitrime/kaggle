from sklearn.preprocessing import StandardScaler
import numpy as np

def parse_features(featuresfile, is_training):
    samples, words, targets, ids = [], [], [], []
    with open(featuresfile, 'r') as f:
        for line in f:
            vec = line.split("\t")
            word = vec[0] 

            tfidf = float(vec[1])
            #tf_hi    = int(0.9 <= tfidf <= 1.0)
            #tf_midhi = int(0.7 <= tfidf <  0.9)
            #tf_midlo = int(0.3 <= tfidf <  0.7)
            #tf_lo    = int(0.1 <= tfidf <  0.3)

            intitle  = int(vec[2])
            punct    = int(vec[3])
            digits   = int(vec[4])
            allcaps  = int(vec[5])
            dashed   = int(vec[6])
            senstart = int(vec[7])
            senend   = int(vec[8])
            relfirst = int(vec[9])

            sample = [tfidf, intitle, punct, digits, allcaps, dashed, senstart, senend, relfirst]

            if is_training:
                target = (vec[10])
                samples.append(sample)
                words.append(word)
                targets.append(target)
            else:
                id = (vec[10])
                samples.append(sample)
                words.append(word)
                ids.append(id)
    if is_training:
        return words, samples, targets
    else:
        return words, samples, ids

if __name__ == '__main__':
    dr = 'data/'
    trainfeatures = 'features-train.csv'
    testfeatures = 'features-test.csv'

    words, samples, targets = parse_features(dr+trainfeatures, True)
    samples = StandardScaler().fit_transform(samples)
    with open(dr+'scaled'+trainfeatures, 'w') as g:
        for i in range(len(words)):
            g.write(words[i]+"\t"+"\t".join([str(x) for x in samples[i]])+"\t"+targets[i])

    words, samples, ids = parse_features(dr+testfeatures, True)
    samples = StandardScaler().fit_transform(samples)
    with open(dr+'scaled'+testfeatures, 'w') as g:
        for i in range(len(words)):
            g.write(words[i]+"\t"+"\t".join([str(x) for x in samples[i]])+"\t"+ids[i])

