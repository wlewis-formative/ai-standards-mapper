#!/usr/bin/env bash

if [[ "$#" -ne 3 ]]
then
  echo 'Usage: ./us.sh <state> <subject-tag> <subject>'
  exit 1
fi

state=$1
tag=$2
subject=$3
echo Generating "$tag" embeddings for "$state" "$subject"

source="{ \"type\": \"csp-api\", \"jurisdiction\": \""$state"\", \"subject\": \""$subject"\" }"
python -m mapper.embed -o embeddings/"$state"."$tag".csv -s "$source"
