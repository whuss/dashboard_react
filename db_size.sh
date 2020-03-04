#! /bin/bash
ROOT_DIR=$(dirname "$0")
cd $ROOT_DIR

source ~/.virtualenvs/infinity/bin/activate

./db_size.py