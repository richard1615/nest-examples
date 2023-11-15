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

# Add arguments for specifying flow length, and delay
parser.add_argument('--length', type=int, default=200, help="Duration of a flow in seconds")
parser.add_argument('--delay', type=int, default=50, help="Delay each flow by specified time in seconds")

# Parse the argument
args = parser.parse_args()
length, delay = args.length, args.delay

# This program emulates point to point networks that connect four hosts: `h1`
# - `h4` via two routers `r1` and `r2`. Two TCP flows are configured between h1 and h3 as well as h2 and h4. 
# The links `h1` <--> `r1`, `h2` <--> `r1`, and `r2` <--> `h3`, `r2` <--> `h4` 
# are edge links. The link `r1` <--> `r2` is the bottleneck link with lesser 
# bandwidth and higher propagation delays.

##############################################################################
#                              Network Topology                              #
#                                                                            #
#    <- 1000mbit, 1ms ->                              <- 1000mbit, 1ms ->    #
# h1 --------------------|                          |-------------------- h3 #
#                        |                          |                        #
#                        |    <- 10mbit, 10ms ->    |                        #
#                         r1 -------------------- r2                         #
#                        |                          |                        #
#                        |                          |                        #
# h2 --------------------|                          |-------------------- h4 #
#    <- 1000mbit, 1ms ->                              <- 1000mbit, 1ms ->    #
#                                                                            #
##############################################################################
# This program runs for 500 seconds (default) and creates a new directory called
# `TCP 4 up squarewave(date-timestamp)_dump`. It contains a `README` that
# provides details about the sub-directories and files within this directory.
# See the plots in `netperf`, `ping` and `ss` sub-directories for this program.
# Refer https://github.com/tohojo/flent/blob/master/flent/tests/tcp_4up_squarewave.conf
# for equivalent Flent config flie.

# Create four hosts `h1` to `h4`, and two routers `r1` and `r2`
h1 = Node("h1")
h2 = Node("h2")
h3 = Node("h3")
h4 = Node("h4")
r1 = Router("r1")
r2 = Router("r2")

# Set the IPv4 address for the networks
n1 = Network("192.168.1.0/24")  # network consisting `h1` and `r1`
n2 = Network("192.168.2.0/24")  # network consisting `h2` and `r1`
n3 = Network("192.168.3.0/24")  # network between two routers
n4 = Network("192.168.4.0/24")  # network consisting `r2` and `h3`
n5 = Network("192.168.5.0/24")  # network consisting `r2` and `h4`

# Connect `h1` and `h2` to `r1`, `r1` to `r2`, and then `r2` to `h3` and `h4`.
# `eth1` to `eth4` are the interfaces at `h1` to `h4`, respectively.
# `etr1a`, `etr1b` and `etr1c` are three interfaces at `r1` that connect it
# with `h1`, `h2` and `r2`, respectively.
# `etr2a`, `etr2b` and `etr2c` are three interfaces at `r2` that connect it
# with `r1`, `h3` and `h4`, respectively.
(eth1, etr1a) = connect(h1, r1, network=n1)
(eth2, etr1b) = connect(h2, r1, network=n2)
(etr1c, etr2a) = connect(r1, r2, network=n3)
(etr2b, eth3) = connect(r2, h3, network=n4)
(etr2c, eth4) = connect(r2, h4, network=n5)

# Assign IPv4 addresses to all the interfaces in the network.
AddressHelper.assign_addresses()

# Set the link attributes: `h1` and `h2` --> `r1` --> `r2` --> `h3` and `h4`
eth1.set_attributes("1000mbit", "1ms")  # from `h1` to `r1`
eth2.set_attributes("1000mbit", "1ms")  # from `h2` to `r1`
etr1c.set_attributes("10mbit", "10ms")  # from `r1` to `r2`
etr2b.set_attributes("1000mbit", "1ms")  # from `r2` to `h3`
etr2c.set_attributes("1000mbit", "1ms")  # from `r2` to `h4`

# Set the link attributes: `h3` and `h4` --> `r2` --> `r1` --> `h1` and `h2`
eth3.set_attributes("1000mbit", "1ms")  # from `h3` to `r2`
eth4.set_attributes("1000mbit", "1ms")  # from `h4` to `r2`
etr2a.set_attributes("10mbit", "10ms")  # from `r2` to `r1`
etr1a.set_attributes("1000mbit", "1ms")  # from `r1` to `h1`
etr1b.set_attributes("1000mbit", "1ms")  # from `r1` to `h2`

# Set default routes in all the hosts and routers.
h1.add_route("DEFAULT", eth1)
h2.add_route("DEFAULT", eth2)
h3.add_route("DEFAULT", eth3)
h4.add_route("DEFAULT", eth4)
r1.add_route("DEFAULT", etr1c)
r2.add_route("DEFAULT", etr2a)

# Set up an Experiment. This API takes the name of the experiment as a string.
exp = Experiment("TCP 4 up squarewave")

# Configure upload from `h1` to `h3` and from `h2` to `h4`.
flow1 = Flow(h1, h3, eth3.get_address(), 0, length, 1)
flow2 = Flow(h1, h3, eth4.get_address(), delay, length + delay, 1)
flow3 = Flow(h1, h3, eth3.get_address(), delay * 3, length + delay * 3, 1)
flow4 = Flow(h1, h3, eth4.get_address(), delay * 5, length + delay * 5, 1)

exp.add_tcp_flow(flow1, "bbr")
exp.add_tcp_flow(flow2, "cubic")
exp.add_tcp_flow(flow3, "bbr")
exp.add_tcp_flow(flow4, "cubic")

flow5 = Flow(h2, h4, eth3.get_address(), 0, length, 1)
flow6 = Flow(h2, h4, eth4.get_address(), delay, length + delay, 1)
flow7 = Flow(h2, h4, eth3.get_address(), delay * 3, length + delay * 3, 1)
flow8 = Flow(h2, h4, eth4.get_address(), delay * 5, length + delay * 5, 1)

exp.add_tcp_flow(flow5, "bbr")
exp.add_tcp_flow(flow6, "cubic")
exp.add_tcp_flow(flow7, "bbr")
exp.add_tcp_flow(flow8, "cubic")

# Run the experiment
exp.run()
