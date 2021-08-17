#!/bin/bash

. /etc/default/weatherClock

pushd $CLOCK_PATH
git fetch --quiet
if ! git diff origin/next --quiet
then
    echo "Pull changes and reboot"
    git pull
    sudo reboot
fi
popd
