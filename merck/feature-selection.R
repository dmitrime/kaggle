library(randomForest)
library(caret)
library(foreach)
library(doMC)
set.seed(1279)

registerDoMC(cores = 8)
allsubsets = list(
                  c(seq(750, 930, 10)),
                  c(seq(500, 660, 10)),
                  c(seq(500, 710, 10)),
                  c(seq(750, 1000, 10)),
                  c(seq(750, 1010, 10)),
                  c(seq(750, 850, 10)),
                  c(seq(850, 1080, 10)),
                  c(seq(600, 730, 10)),
                  c(seq(600, 700, 10)),
                  c(seq(500, 670, 10)),
                  c(seq(750, 920, 10)),
                  c(seq(750, 910, 10)),
                  c(seq(850, 1030, 10)),
                  c(seq(500, 950, 10)),
                  c(seq(750, 950, 10))
              )
for ( i in c(1:15) ) 
{
    filterFile = paste("../selected/cor9/selected_", i, ".txt", sep='')
    trainFile = paste("../TrainingSet/ACT", i, "_competition_training.csv", sep='')

    dset = read.csv(trainFile, header=TRUE, nrows=100)
    classes = sapply(dset, class)
    dset = read.csv(trainFile, header=TRUE, colClasses=classes)
    colfilters = as.vector(as.matrix(read.table(filterFile, header=FALSE)))
    colfilters = c("MOLECULE", "Act", colfilters)
    train = dset[,colfilters]

    print(trainFile)

    funcs = rfFuncs
    funcs$fit = function(x, y, first, last, ...)
    {
        randomForest(x, y, importance = first, ntree=250, ...)
    }
    ctrl = rfeControl(functions = funcs,
                      method = "cv",
                      verbose = TRUE,
                      #rerank = TRUE,
                      returnResamp = "all")

    subsets = allsubsets[[i]]
    prof    = rfe(train[,3:ncol(train)], train$Act, metric = "Rsquared", sizes = subsets, rfeControl = ctrl)
    print(prof)

    selected = prof$optVariables
    save(prof, file=paste("rfProfile/rfProf_",i,".R", sep=''))
    write(selected, file=paste("rfSelected/rf_selected_",i,".txt", sep=''))
}

