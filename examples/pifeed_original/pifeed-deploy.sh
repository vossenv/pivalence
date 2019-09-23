
#!/usr/bin/env bash



ssh pi@192.168.50.58 'sudo rm -rf /home/pi/Desktop/pifeed/*'


scp feed.py pi@192.168.50.58:/home/pi/Desktop/pifeed/feed-2.0.py
scp datasource.py pi@192.168.50.58:/home/pi/Desktop/pifeed/datasource.py

#sudo kill $(ps aux | grep '[p]ython feed-2.0.py' | awk '{print $2}')