for ( i in c(1:5) ) 
{
    trainFile = paste("parallel/train-features-", i, ".txt", sep='')
    testFile  = paste("parallel/test-features-", i, ".txt", sep='')

    train = read.table(trainFile, header=TRUE)
    print(trainFile)

    model = glm(as.factor(y) ~ ., data=train, family=binomial)
    print(model)

    # predict test
    test = read.table(testFile, header=TRUE)
    result = predict(model, test, type="response")

    submission <- data.frame(result)
    write.table(submission, file=paste("results/results-",i,".txt", sep=''),
                row.names=FALSE, col.names=FALSE, sep=',')
}

