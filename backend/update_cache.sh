#! /bin/bash
ROOT_DIR=$(dirname "$0")
cd $ROOT_DIR

source ~/.virtualenvs/infinity/bin/activate

# update permanent cache
python scripts/cache_queries.py fill 2020-04-01

# update daily cache
python scripts/cache_queries.py update