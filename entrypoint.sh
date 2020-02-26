#!/bin/bash

echo "Docker Container Started"

echo "0 0 * * * wget -O/dev/null 0.0.0.0:5000/poll
# This extra line makes it a valid cron" > scheduler.txt

crontab scheduler.txt
cron 

echo "Cron Job Started"
python ./lostandfound/main.py
