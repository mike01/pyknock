"""
Ultra flexible port knocking deamon which allows triggering actions
on specific network events.
See config.py fore configuration.
"""
import threading
import logging
import os
import socket
from time import time as time_now

from pypacker import psocket
from pypacker.layer12 import ethernet

logger = logging.getLogger("pyknock")
# logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

logger_streamhandler = logging.StreamHandler()
logger_formatter = logging.Formatter("%(asctime)s: %(levelname)s: %(message)s")
logger_streamhandler.setFormatter(logger_formatter)

logger.addHandler(logger_streamhandler)

logger_filehandler = logging.FileHandler(CURRENT_DIR + "/logs.txt")
logger_filehandler.setFormatter(logger_formatter)
logger.addHandler(logger_filehandler)

try:
	import config
except:
	logger.warning("could not find %r in pyknock directiry. Please create it before starting!" % "config.py")
	os.exit(1)

class KnockLogic(object):
	def __init__(self, trigger_strategies,
			timeout_reset_sec=5,
			iface_name=None):
		self._iface_name = iface_name
		self._timeout_reset_sec = timeout_reset_sec
		self._time_last_match = 0
		self._state_active = False
		self._socket = None
		self._trigger_strategies = trigger_strategies
		self._trigger_strategy_active = None
		self._state_idx = 0

	def set_state(self, state_active=True):
		if self._state_active == state_active:
			# nothing changed
			logger.warning("no new state, doing nothing")
			return

		if not state_active:
			self._state_active = False
			self._socket.close()
		else:
			logger.debug("opening socket")
			self._socket = psocket.SocketHndl(iface_name=self._iface_name)
			self._responder_thread = threading.Thread(
				target=KnockLogic._listen_cycler,
				args=[self, self._socket])
			self._state_active = True
			self._responder_thread.start()

	def _reset_condition(obj):
		logger.debug("resetting state %d to 0" % obj._state_idx)
		obj._state_idx = 0
		obj._trigger_strategy_active = None

	def _listen_cycler(obj, sock):
		logger.debug("starting listen cycler")

		while obj._state_active:
			try:
				bts = sock.recv()
				pkt = ethernet.Ethernet(bts)

				if obj._trigger_strategy_active is not None and\
					(time_now() - obj._time_last_match) > obj._timeout_reset_sec:
					KnockLogic._reset_condition(obj)

				# initial state or reset
				if obj._trigger_strategy_active is None:
					for cond_idx, strategy in enumerate(obj._trigger_strategies):
						if strategy[0](pkt):
							logger.info("found initial matching condition at strategy index %d" % cond_idx)
							obj._state_idx = 1
							obj._trigger_strategy_active = strategy
							obj._time_last_match = time_now()
							break
				# some condition matched before
				elif obj._trigger_strategy_active[obj._state_idx](pkt):
					logger.info("state %d/%d matched" %
						(obj._state_idx + 1, len(obj._trigger_strategy_active)-1))
					obj._state_idx += 1
					obj._time_last_match = time_now()

				if obj._trigger_strategy_active is None:
					continue

				# -1 because last element is action callback
				if obj._state_idx >= len(obj._trigger_strategy_active) - 1:
					logger.info("triggering action!")
					obj._trigger_strategy_active[-1](pkt)
					KnockLogic._reset_condition(obj)
			except socket.timeout:
				# try next packet
				logger.debug("timeout...")
			except OSError:
				break
			except AttributeError:
				pass
			except Exception as ex:
				logger.debug("exception while parsing: %r" % ex)

if __name__ == "__main__":
	timeout = config.TIMEOUT_RESET_SEC
	iface_name = config.IFACE_NAME

	knocklogic = KnockLogic(config.TRIGGER_STRATEGIES, timeout_reset_sec=timeout)
	knocklogic.set_state(state_active=True)
	logger.info("starting to listen, press enter to exit")
	input()
	knocklogic.set_state(state_active=False)