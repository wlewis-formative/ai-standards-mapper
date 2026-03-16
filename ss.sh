#!/usr/bin/env bash

if [[ "$#" -ne 1 ]]
then
  echo 'Usage: ./ss.sh <state>'
  exit 1
fi

echo Building social studies mappings for "$1"

for state in "California" "Florida" "Illinois" "New York"
do
  python -m mapper.map -c "embeddings/$state.social-studies.csv" -m "embeddings/$1.hs-social-studies.csv" -o mappings
done
