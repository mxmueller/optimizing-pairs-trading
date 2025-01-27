#!/bin/bash
chmod +x "$0"

dir="../notebooks/strategies"
total=$(ls "$dir"/*.ipynb 2>/dev/null | wc -l)
current=0

for notebook in "$dir"/*.ipynb; do
    ((current++))
    echo -ne "\rProcessing notebooks: ${current}/${total} [$(printf "%3d%%" $((current*100/total)))]"
    jupyter nbconvert --execute --to notebook --inplace "$notebook" >/dev/null 2>&1
done

echo -e "\nDone!"