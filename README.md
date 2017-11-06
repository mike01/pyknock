### General information
Pyknock is a Python based ultra flexible port knocking daemon.
The Pyknock deamon listens for a special knock sequence of packets and
triggers an action if the sequence matches. Knock sequences and actions
are defined in simple python script named (see `config.py`).
Rules are not limited to UDP/TCP ports, any readable network value can
be used for this like IP ids, IP source addresses, packet contents, checksums etc.

### Prerequisites
- python 3.x
- pypacker

### Installation
Just download/unpack

### Usage
  * Define conditions and actions in config.py in same directoy.
  * Start knock deamon

  `python pyknock.py`

  * Send knock sequence via client (e.g. hping)

### Example
The following example callflow is used to open and again close a SSH port.

  * Client sends two TCP packet with target port 1337 and 1338 and a third packet with IP id 69
  * Server detects sequence and adds iptables rules to open TCP-port 22
  * Client can now connect via SSH
  * After client has finished it sends thre UDP packets in sequence having destination ports 1339, 1340 and 1341
  * Server detects sequence and closes TCP-port 22