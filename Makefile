# detatch run
run:
	nohup python3 bot.py > output.log 2>&1 &
stop:
	pkill -f python