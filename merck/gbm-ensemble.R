library(gbm)
set.seed(1173)

treelist = list(20000, 5500, 3800, 3800, 3500, 20000, 6000, 8500,
                10000, 12000, 12000, 12000, 9500, 9600, 8000)
for ( take in c(1:32) ) 
{
    for ( i in c(1:15) ) 
    {
        trainFile = paste("../../TrainingSet/ACT", i, "_competition_training.csv", sep='')
        testFile = paste("../../TestSet/ACT", i, "_competition_test.csv", sep='')
        filterFile = paste("../../selected/more_ensemble/sel",take,"/mix3_selected_", i, ".txt", sep='')

        dset = read.csv(trainFile, header=TRUE, nrows=100)
        classes = sapply(dset, class)
        dset = read.csv(trainFile, header=TRUE, colClasses=classes)
        colfilters = as.vector(as.matrix(read.table(filterFile, header=FALSE)))
        train = dset[, c("Act", colfilters)]
        train.form = as.formula(paste("Act ~ ", paste(colfilters, collapse=" + ")))

        print(trainFile)

        trees = treelist[[i]]
        model = gbm(train.form, data=train,
                    distribution="gaussian",
                    n.trees = trees,
                    interaction.depth = 10, 
                    shrinkage = 0.01)

        #predict test
        test = read.csv(testFile, header=TRUE)
        result = predict(model, newdata=test, trees)

        submission <- data.frame(test$MOLECULE, result)
        write.table(submission, file=paste("gbmSubmissions/take",take,"/gbm_submission_",i,".csv", sep=''),
                    row.names=FALSE, col.names=FALSE, sep=',')
    }
}

