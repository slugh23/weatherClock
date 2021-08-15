. /etc/default/weatherClock

matchbox-window-manager -use_titlebar no -use_cursor no -use_desktop_mode plain &
python3 $CLOCK_PATH/weatherClock.py
