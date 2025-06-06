# detatch run
run:
	nohup python3 bot.py > output.log 2>&1 &
stop:
	pkill -f python
mockon:
	export USE_PLACEHOLDER=true
mockoff:
	export USE_PLACEHOLDER=false