import time
import signal
import logging


log = logging.getLogger(__name__)
name = None
done = False


def request_exit(signum, frame):
    global done
    log.info('Stopping the %s...', name)
    done = True


def run(cmd_name, f_init, f_stop, f_loop, *args, f_loop_delay_ms=3000):
    global name
    name = cmd_name
    log.info('Starting the %s', name)
    #
    signal.signal(signal.SIGINT, request_exit)
    signal.signal(signal.SIGTERM, request_exit)
    #
    f_init(*args)
    #
    call_loop = f_loop is not None
    while(not done):
        if call_loop:
            call_loop = f_loop()
        time.sleep(f_loop_delay_ms/1000.0)
    #
    f_stop()
    log.info('Stopped the %s', name)
