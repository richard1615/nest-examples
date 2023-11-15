# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest.experiment import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper
import argparse

# Create the parser
parser = argparse.ArgumentParser()

# Add an argument
parser.add_argument('--tcp', type=str, default="cubic", help="TCP algorithm to use")
parser.add_argument('--qdisc', type=str, default="", help= "Queue discipline")

# Parse the argument
args = parser.parse_args()


# This program emulates point to point networks that connect a single source h1
# and 5 hosts on the destination. 5 TCP flows are configured to each host, along
# with 2 UDP flows. This test is useful for stress testing and qdisc evaluation.

##############################################################################
#                              Network Topology                              #
#                                                                            #
#                                                     <- 1000mbit, 1ms ->    #
#                                                   |-------------------- h2 #
#                                                   |       tcp_algo         #
#                             <- 10mbit, 10ms ->    |                        #
# h1 -------------------- r1 -------------------- r2            .            #
#      tcp_algo                                     |           .            #
#	                                            |         5 hosts
#                                                   |           .            #
#                                                   |           .            #
#                                                   |   tcp_algo             #
#                                                   |-------------------- h5 #
#                                                     <- 1000mbit, 1ms ->    #
#                                                                            #
##############################################################################

# This program runs for 200 seconds and creates a new directory called
# `choke-point-to-point(date-timestamp)_dump`. It contains a `README` that
# provides details about the sub-directories and files within this directory.
# See the plots in `netperf`, `ping` and `ss` sub-directories for this program.

# Create four hosts `h1` to `h4`, and two routers `r1` and `r2`
h1 = Node("h1")
h2 = Node("h2")
h3 = Node("h3")
h4 = Node("h4")
h5 = Node("h5")
h6 = Node("h6")
r1 = Router("r1")
r2 = Router("r2")

# Set the IPv4 address for the networks
n1 = Network("192.168.1.0/24")  # network consisting `h1` and `r1`
n2 = Network("192.168.2.0/24")  # network between two routers
n3 = Network("192.168.3.0/24")  # network consisting `r2` and `h2`
n4 = Network("192.168.4.0/24")  # network consisting `r2` and `h3`
n5 = Network("192.168.5.0/24")  # network consisting `r2` and `h4`
n6 = Network("192.168.6.0/24")  # network consisting `r2` and `h5`
n7 = Network("192.168.7.0/24")  # network consisting `r2` and `h6`

# Connect `h1` and `h2` to `r1`, `r1` to `r2`, and then `r2` to `h3` and `h4`.
# `eth1` to `eth4` are the interfaces at `h1` to `h4`, respectively.
# `etr1a`, `etr1b` and `etr1c` are three interfaces at `r1` that connect it
# with `h1`, `h2` and `r2`, respectively.
# `etr2a`, `etr2b` and `etr2c` are three interfaces at `r2` that connect it
# with `r1`, `h3` and `h4`, respectively.
(eth1, etr1a) = connect(h1, r1, network=n1)
(etr1b, etr2a) = connect(r1, r2, network=n2)
(etr2b, eth2) = connect(r2, h2, network=n3)
(etr2c, eth3) = connect(r2, h3, network=n4)
(etr2d, eth4) = connect(r2, h4, network=n5)
(etr2e, eth5) = connect(r2, h5, network=n6)
(etr2f, eth6) = connect(r2, h6, network=n7)

# Assign IPv4 addresses to all the interfaces in the network.
AddressHelper.assign_addresses()

if args.qdisc:

	if args.qdisc == 'choke':
		# Configure the parameters of `choke` qdisc.  For more details about `choke`
		# in Linux, use this command on CLI: `man tc-choke`.
		qdisc = "choke"
		qdisc_parameters = {
		    "limit": "100",  # set the queue capacity to 100 packets
		    "min": "5",  # set the minimum threshold to 5 packets
		    "max": "15",  # set the maximum threshold to 15 packets
		}
		
	elif args.qdisc == 'pfifo':
		# Configure the parameters of `pfifo` qdisc.  For more details about `pfifo`
		# in Linux, use this command on CLI: `man tc-pfifo`.
		qdisc = "pfifo"
		qdisc_parameters = {"limit": "100"}  # set the queue capacity to 100 packets
		
	elif args.qdisc == "codel":
		qdisc = "codel"
		qdisc_parameters = {
	    		"limit": "1000",  # set the queue size to 1000 packets (default is 1000)
	    		"target": "10000ms",  # set the target queue delay to 10000ms (default is 5ms)
	    		"interval": "100ms",  # set the interval value to 100ms (default is 100ms)
	    		"ce_threshold": "40ms",  # ce_threshold = (17% of queue size in pckts * size of each packet * 8) / (bandwidth)
	    		"ecn": "",  # enables ecn marking for codel
		}
			
	elif args.qdisc == "pie":
		# Configure the parameters of `pie` qdisc.  For more details about `pie`
		# in Linux, use this command on CLI: `man tc-pie`.
		qdisc = "pie"
		qdisc_parameters = {
		    "limit": "100",  # set the queue capacity to 100 packets
		    "target": "2ms",  # set the target queue delay to 2ms (default is 15ms)
		}
	elif args.qdisc == "red":
		# Configure the parameters of `red` qdisc.  For more details about `red`
		# in Linux, use this command on CLI: `man tc-red`.
		qdisc = "red"
		qdisc_parameters = {
		    "limit": "150000",  # set the queue capacity to 150000 bytes
		    "min": "7500",  # set the minimum threshold to 7500 bytes
		    "max": "22500",  # set the maximum threshold to 22500 bytes
		}
	etr1b.set_attributes("10mbit", "10ms", qdisc, **qdisc_parameters)  # Setting link attributes from `r1` to `r2`
else:
	etr1b.set_attributes("10mbit", "10ms")  # Setting link attributes from `r1` to `r2`

# Set the link attributes: `h1`--> `r1` --> `r2` --> `h2`, `h3`, h4`, `h5`, `h6`
eth1.set_attributes("1000mbit", "1ms")  # from `h1` to `r1``
etr2b.set_attributes("1000mbit", "1ms")  # from `r2` to `h2`
etr2c.set_attributes("1000mbit", "1ms")  # from `r2` to `h3`
etr2d.set_attributes("1000mbit", "1ms")  # from `r2` to `h4`
etr2e.set_attributes("1000mbit", "1ms")  # from `r2` to `h5`
etr2f.set_attributes("1000mbit", "1ms")  # from `r2` to `h6`

# Set the link attributes: `h1`, `h2`,`h3`, `h4`, `h5` --> `r2` --> `r1` --> `h1`
eth2.set_attributes("1000mbit", "1ms")  # from `h2` to `r2`
eth3.set_attributes("1000mbit", "1ms")  # from `h3` to `r2`
eth4.set_attributes("1000mbit", "1ms")  # from `h4` to `r2`
eth5.set_attributes("1000mbit", "1ms")  # from `h5` to `r2`
eth6.set_attributes("1000mbit", "1ms")  # from `h6` to `r2`
etr2a.set_attributes("10mbit", "10ms")  # from `r2` to `r1`
etr1a.set_attributes("1000mbit", "1ms")  # from `r1` to `h1`

# Set default routes in all the hosts and routers.
h1.add_route("DEFAULT", eth1)
h2.add_route("DEFAULT", eth2)
h3.add_route("DEFAULT", eth3)
h4.add_route("DEFAULT", eth4)
h5.add_route("DEFAULT", eth5)
h6.add_route("DEFAULT", eth6)
r1.add_route("DEFAULT", etr1b)
r2.add_route("DEFAULT", etr2a)

# Set up an Experiment. This API takes the name of the experiment as a string.
exp = Experiment("cisco-5tcpup-2udpflood-conf")

# Configure two flows from `h1` to `h3` and two more flows from `h2` to `h4`.

# 5 TCP upload flows
flow1 = Flow(h1, h2, eth2.get_address(), 0, 200, 1)
flow2 = Flow(h1, h3, eth3.get_address(), 0, 200, 1)
flow3 = Flow(h1, h4, eth4.get_address(), 0, 200, 1)
flow4 = Flow(h1, h5, eth5.get_address(), 0, 200, 1)
flow5 = Flow(h1, h6, eth6.get_address(), 0, 200, 1)

# 2 UDP 6 Mbit flows
flow6 = Flow(h1, h2, eth2.get_address(), 0, 200, 1)
flow7 = Flow(h1, h3, eth3.get_address(), 0, 200, 1)

exp.add_tcp_flow(flow1, args.tcp)
exp.add_tcp_flow(flow2, args.tcp)
exp.add_tcp_flow(flow3, args.tcp)
exp.add_tcp_flow(flow4, args.tcp)
exp.add_tcp_flow(flow5, args.tcp)
exp.add_udp_flow(flow6, '6mbit')
exp.add_udp_flow(flow7, '6mbit')


# Run the experiment
exp.run()
