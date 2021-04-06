# create emulator instance for creating sessions and utility methods
import random
import time
from datetime import datetime, timedelta
import csv
import typing

from core import errors
from core.emulator.coreemu import CoreEmu
from core.emulator.data import NodeOptions, IpPrefixes
from core.emulator.enumerations import EventTypes
from core.location.mobility import BasicRangeModel
from core.nodes.network import WlanNode

from NodeWrapper import NodeWrapper

coreemu = CoreEmu()
session = coreemu.create_session()
session.set_state(EventTypes.CONFIGURATION_STATE)


# Number of nodes on the network
num_nodes = 10

packet_size = 1 * 1024

packet_freq = 10

sim_time = 60 * 30

port = 5000

packets_per_pulse = 1

# List of all nodes in the simulation
nodes = []

# Node : packets sent to from other nodes
packet_rec: typing.Dict[NodeWrapper, int] = {}

# Node : (sent, received)
results: typing.Dict[NodeWrapper, typing.Tuple[int, int]] = {}

# IP prefix generator
ip_prefixes = IpPrefixes(ip4_prefix="10.0.0.0/24")

# Create a WLAN
wlan = session.add_node(WlanNode, options=NodeOptions(x=200, y=200))

# Configuring wlan
session.mobility.set_model_config(
    wlan.id,
    BasicRangeModel.name,
    {
        "range": "28000000",  # in pixels
        "bandwidth": "64000",  # in bits per second
        "delay": "0",  # in microseconds
        "error": 0,  # loss percentage
        "jitter": 0  # in microseconds
    },
)

print("-------- CREATING NODES --------")
for x in range(num_nodes):
    nodes.append(NodeWrapper(session).add_node(x=200 + 1 * x, y=200 + 1 * x).link_wlan(ip_prefixes, wlan))

session.instantiate()


print("-------- SETUP --------")

time.sleep(60 * 0.5)


x = nodes[-1].node.cmd(f"vtysh -c 'show ip ospf neighbor'")
print("\nOSPF Neighbours:", len(x.splitlines()) - 1)

x = nodes[1].node.cmd(f"vtysh -c 'show ip ospf neighbor'")
print("\nOSPF Neighbours:", len(x.splitlines()) - 1)


print("-------- STARTING SIMULATION --------")

end = datetime.now() + timedelta(seconds=sim_time)

iters: int = 1

while datetime.now() < end:
    print("- Pulse ", iters * packet_freq, " / ", sim_time)

    for node in nodes:

        for x in range(packets_per_pulse):
            dest = random.choice(nodes)
            node.send_udp(destination=dest.ip_addr, port=port, size=packet_size, debug=False)

            if dest in packet_rec:
                packet_rec[dest] += 1
            else:
                packet_rec[dest] = 1

    iters += 1
    time.sleep(packet_freq)

print("-------- DONE --------")


print("-------- PROCESSING --------")

with open('/home/jack/nodes_%s.csv' % num_nodes, 'w') as f:
    for node in nodes:

        output = ""

        try:
            output = node.read_capture(port=5000)
        except errors.CoreCommandError as x:
            output = str(x)

        try:
            lines = output.splitlines()
            lines = list(filter(lambda line: "%s.%i: UDP" % (node.node.name, port) in line, lines))

            #print("(", node.node.name, ") ", "Sent: ", packet_rec[node], " Received: ", len(lines))
            results[node] = (packet_rec[node], len(lines))
            f.write("%s, %i, %i \n" % (node.node.name, packet_rec[node], len(lines)))

        except KeyError as e:
            print(e)

# Write the results to a CSV file

input("Press any key to continue...")

session.shutdown()

# stop session
