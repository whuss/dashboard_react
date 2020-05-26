#! /bin/sh

export PORT=8003

tmux new-session -d -s dashboard npm run start
