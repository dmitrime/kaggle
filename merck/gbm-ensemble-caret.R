library(caret)
library(foreach)
library(doMC)
set.seed(1173)

registerDoMC(cores = 8)
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
        train = dset[,colfilters]
        print(trainFile)

        fitCtrl = trainControl(method = "cv",
                               verbose = TRUE,
                               returnResamp = "all")

        gbmGrid = expand.grid(.interaction.depth = 10, .n.trees = seq(3000, 12000, 200), .shrinkage = c(0.01))
        model = train(train, dset$Act, method='gbm',
                      metric   = "Rsquared",
                      tuneGrid = gbmGrid,
                      trControl = fitCtrl,
                      verbose = FALSE)
        print(model)

        #predict test
        test = read.csv(testFile, header=TRUE)
        result = predict(model, test[,colfilters], type="raw")

        submission <- data.frame(test$MOLECULE, result)
        write.table(submission, file=paste("gbmSubmissions/take",take,"/gbm_submission_",i,".csv", sep=''),
                    row.names=FALSE, col.names=FALSE, sep=',')
    }
}

