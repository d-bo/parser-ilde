#!/bin/bash

# mongodb prefix
# python step2-3 will catch this
export ILDE_MONGO_DB="parser"

echo -e "\e[44mSTART ILDE\e[0m"
start=`date +%s`
node step1.js
python step2.py
python step25.py
python step3.py
end=`date +%s`

runtime=$((end-start))
echo -e "\e[42mILDE FINISHED\e[0m"
echo "Script exec time: $runtime"
