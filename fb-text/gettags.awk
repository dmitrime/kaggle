#!/bin/bash

if [ -z "$1" ] ; then
    echo "Extracts the tags column from the input, split by space, sort by frequency and write using \"count,tag\" format into tags.csv"
    echo "usage: $0 input.csv"
    exit 1;
fi

#cat $1 | sed "s/<code>.*<\/code>//" | sed "s/<pre>.*<\/pre>//" | sed "s/<script>.*<\/script>//" | sed "s/<a href.*<\/a>//" | sed "s/<img.*>//" | awk -F "\",\"" 'NR > 1 {print $4}' | tr -d '\"' | sed "s/<.*>.*<.*>//" | tr -s [:space:] '\n' | sort -f | uniq -c -i | sort -n -r > tags.csv
cat $1 | sed "s/<.*>.*<\/.*>//" | sed "s/<img.*>//" | awk -F "\",\"" 'NR > 1 {print $4}' | tr -d '\"' | sed "s/<.*>.*<.*>//" | tr -s [:space:] '\n' | sort -f | uniq -c -i | sort -n -r > tags.csv

