Overview of stats collected
===========================

This README contains general information about stats collected by NeST.
You can disable generation of this file by setting config value of
'readme_in_stats_folder' to False in NeST.

This folder contains JSON files and sub-folders containing plots. The JSON
file contains timestamped data collected by NeST. Of course, this is
not meant to be read by you. It is provided in case you would like to
generate your own custom plots from the data provided by NeST.

The sub-folders (netperf/, ping/, etc) contain plots. These plots are
made from their respective JSON files. For example, plots inside netperf/
folder are based on data in netperf.json file.

Below, we give a brief description of plots in each sub-folder.

NOTE: All the below sub-folders may not be present in this folder.
The sub-folders present depend on the experiment being run and the stats
requested from NeST.

netperf/
--------
NeST internally uses netperf to generate TCP traffic. The netperf
folder contains the plots for sending rate of the network traffic.

Note that the *sending rate* is the rate at which sender is sending packets. Hence,
this can at times be higher than the bottleneck bandwidth.

iperf3/
-------
NeST internally uses iperf3 to generate UDP traffic. Similar to
netperf, this folder also contains plots for sending rate of network traffic.

ping/
-----
As the name suggests, it provides plots based on data obtained from ping
tool. The plots visualize the round trip time over time.

ss/
---
ss is short for "socket stats" and it visualizes data obtained from ss
utility. The plots visualize various TCP parameters like:

* CWND - Congestion windown
* Delivery rate
* rtt - Round Trip Time (as seen by TCP)
* dev_rtt - Deviation in rtt
* ssthresh

tc/
---
tc is short for "traffic control" and it visualizes data obtained from tc
utility. The data visualized pertain to various queueing discipline
parameters.

Below are some of the parameters visualized in these plots:
* Queue length over time
* Packet drops over time
