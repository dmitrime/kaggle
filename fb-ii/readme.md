FB-II
====

My Kaggle's FB-II competition submission.

Cleaning uses regexps, sorting and similarity hashing with thresholds and rules. It adds strings into the disjoint sets structure and merges two sets if they are similar (same ASN).

Prediction part extracts features related to the optimal paths in the previous graphs and uses logistic regression to produce final results.
