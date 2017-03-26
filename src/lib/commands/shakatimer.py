import time
import thread

exit_flag = 0
timer_running = False

def shakatimer(viewer, args):
	#usage = '!shakatimer <timer>'
	global exit_flag
	global timer_running

	if viewer != 'shakajiub':
		return "you cannot do that!"

	if not args[0].isdigit():
		return "that's not an integer!"
	timer = int(args[0])

	print 'called timer: %s' % timer

	if timer == 0 and exit_flag == 0:
		exit_flag = 1
		return "cancelling the timer!"
	if not 0 < timer < 21:
		return "timer not in acceptable range!"

	if timer_running:
		return "a timer is already running!"

	try: thread.start_new_thread(shakatimer_thread, (viewer, timer))
	except: return "couldn't start timer!"

	return "started a timer for %s minutes!" % timer

def shakatimer_thread(viewer, timer):
	global exit_flag
	global timer_running

	timer_running = True

	while timer > 0:
		if exit_flag:
			break
		time.sleep(10)
		timer -= 1
		#serve.bot.irc.send_message('#shakajiub', 'test')

	exit_flag = 0
	timer_running = False
