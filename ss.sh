#!/usr/bin/env bash

echo Building social studies mappings for "$1"

for state in "California" "Florida" "Illinois" "New York"
do
  python -m mapper.map -c "embeddings/$state.social-studies.csv" -m "embeddings/$1.social-studies.csv" -o mappings
done
