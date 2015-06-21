#!/bin/sh
python3 /home/allenwhale/srv/kkbox_vs_spotify/server.py&
sleep 3
curl http://localhost:12345
sleep 10
