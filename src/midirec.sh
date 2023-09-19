#!/bin/bash
# Windows start script for midirec.py https://gitlab.com/bob-ros2/midistuff

echo -n "Do you want to start a single track recording (0) or record multiple tracks (1)? Choose 0 or 1: "
read in

if [ "$in" = "0" ]; then
  python midirec.py
elif [ "$in" = "1" ]; then
  python midirec.py -a 30
fi
