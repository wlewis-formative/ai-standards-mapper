#!/usr/bin/env bash

if [[ "$#" -ne 3 ]]
then
  echo 'Usage: ./state.sh <state> <science-subject> <ss-subject>'
  exit 1
fi

state=$1
science_sub=$2
ss_sub=$3

make_source () {
  local state=$1
  local subject=$2
  echo "{\"type\":\"csp-api\",\"jurisdiction\":\"$state\",\"subject\":\"$subject\"}"
}

echo "Creating embeddings for $state $science_sub"
python -m mapper.embed --output "embeddings/$state.science.csv" --source "$(make_source "$state" "$science_sub")"

echo "Creating embeddings for $state $ss_sub"
python -m mapper.embed --output "embeddings/$state.social-studies.csv" --source "$(make_source "$state" "$ss_sub")"

echo "Generating science mappings"
python -m mapper.map \
  --core-standard-set "embeddings/NGSS.science.csv" \
  --mapped-standard-set "embeddings/$state.science.csv" \
  --output mappings

echo "Generating social studies mappings"
for core_state in "California" "Florida" "Illinois" "New York"
do
  python -m mapper.map \
    --core-standard-set "embeddings/$core_state.social-studies.csv" \
    --mapped-standard-set "embeddings/$state.social-studies.csv" \
    --output mappings
done
