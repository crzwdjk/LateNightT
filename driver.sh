#!/bin/bash
set -e

python3 drawmap.py
for i in *.png
do 
    echo $i
    pngtopnm $i | pnmquant 256 | ppmtogif > `basename $i .png`.gif
done
gifsicle --delay 100 --loopcount --colors 256 ridership-2*.gif > mbta-night.gif
