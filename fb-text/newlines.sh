#!/bin/bash

if [ -z "$1" ] ; then
    echo "First removes all the \\n then replaces all the \\r with \\n"
    echo "usage: $0 input.csv output.csv"
    exit 1;
fi

tr '\n' ' ' < "$1" | tr '\r' '\n' > "$2"

