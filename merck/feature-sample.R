for ( t in c(1:32) ) 
{
    set.seed(1380+t)
    print("------------------------")
    print(paste("Run number ", t))
    for ( i in c(1:15) ) 
    {
        good = read.table(paste("../filtering/good_", i, ".txt", sep=''))
        sel1 = read.table(paste("../selected_", i, ".txt", sep=''))
        sel2 = read.table(paste("../rf/rf_selected_", i, ".txt", sep=''))

        avlen = as.integer((length(sel1$V1)+length(sel2$V1)) / 2)
        unite = union(sel1$V1, sel2$V1)
        restr = setdiff(good$V1, unite)

        take1 = unique(sample(unite, as.integer(avlen), replace=T))
        take2 = sample(restr, min(length(take1), length(restr)), replace=F)

        total = c(take1, take2)
        print(paste("take1: ", length(take1), "(", length(unite), "), take2: ", length(take2), "(", length(restr),
                    ") | total = ", length(total)))

        write(total, file=paste("sel",t,"/mix_selected_",i,".txt", sep=''))
    }
}

