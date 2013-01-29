Kaggle TSP
==========

My python scripts for Kaggle's Travelling Santa Problem (kaggle.com/c/traveling-santa-problem).

naive.py -- naive greedy computation of the first path.
distance.py -- for every city computes the 25 closest cities and saves them into separate files 'bestN_dist.csv'.
two_opt_closest.py -- 2-opt heuristic implementation that scans only the city's 25 closest neighbours from the bestN_dist.csv files.
greedy.py -- takes the first path from the naive script and runs 2-opt on it. Then builds the second path in a way similar to the naive solution, but using only the 25 bestN_dist.csv files. Runs 2-opt on the second path.
three_opt_closest.py -- 3-opt heuristic implementation that scans only the city's 25 closest neighbours from the bestN_dist.csv files. Takes the result produced by greedy.py and runs 3-opt on the second path.
balance.py -- Takes the output of three_opt_closest.py and tries to balance the two paths by deleting X random edges from the second path and reconnecting it in a worst way. Then runs 2-opt on the second path in order to improve it with deleted edges from the first path. As a result the two paths are more balanced, the first path gets longer and the second shorter.

My final position was 150th with a score of 7,253,142 out of 356 participants. 

