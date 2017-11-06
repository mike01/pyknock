"""
Default configuration.
Test via:
- python pyknock.py
- hping -p 1337 -c 1 localhost;hping -p 1338 -c 1 localhost;hping -p 1339 -c 1 localhost"
"""
import os
from pypacker.layer3 import ip, icmp
from pypacker.layer4 import tcp, udp


# Conditions to match (return True) if state should be incremented
def condition1(pkt):
	return pkt[tcp.TCP].dport == 1337


def condition2(pkt):
	return pkt[tcp.TCP].dport == 1338


def condition3(pkt):
	return pkt[tcp.TCP].dport == 1339
	#return pkt[udp.UDP].dport == 1339
	#return b"some_special_bytes" in pkt[icmp.ICMP].body_bytes
	#return pkt[ip.IP].dst_s == "192.168.0.1"
	#return pkt[ip.IP].id == 123

# Actions to perform if all conditions in a sequence matched
def action_openport():
	print("action to open port!")
	os.system("iptables -L")


def action_closeport():
	print("action to close port!")
	os.system("iptables -L")

# Conditions to check one after another.
# Last element is the action to execute if all conditions matched.
TRIGGER_SEQUENCE_OPENPORT = [condition1, condition2, condition3, action_openport]
TRIGGER_SEQUENCE_CLOSEPORT = [condition3, condition2, condition1, action_closeport]

# All sequences to be used
TRIGGER_STRATEGIES = [
	TRIGGER_SEQUENCE_OPENPORT,
	TRIGGER_SEQUENCE_CLOSEPORT
]

# State is reset after TIMEOUT_RESET_SEC seconds without incremented state.
TIMEOUT_RESET_SEC = 3
# Interface name to listen on, None=every interface (= more packets = more CPU usage)
IFACE_NAME = None
