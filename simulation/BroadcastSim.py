# create emulator instance for creating sessions and utility methods
import time

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

# List of all nodes in the simulation
nodes = []

# IP prefix generator
ip_prefixes = IpPrefixes(ip4_prefix="10.0.0.0/24")

# Create a WLAN
wlan = session.add_node(WlanNode, options=NodeOptions(x=200, y=200))

# Configuring wlan
session.mobility.set_model_config(
    wlan.id,
    BasicRangeModel.name,
    {
        "range": "28000",  # in pixels
        "bandwidth": "55000000",  # in bits per second
        "delay": "100",  # in microseconds
        "error": 0,  # loss percentage
        "jitter": 0  # in microseconds
    },
)

for x in range(num_nodes):
    nodes.append(NodeWrapper(session).add_node(x=50 + 100 * x, y=20 + 100 * x).link_wlan(ip_prefixes, wlan))

session.instantiate()
print("------ Starting Session ------")

time.sleep(10)

x = nodes[-1].node.cmd(f"vtysh -c 'show ip ospf neighbor'")
print("\n Number of neighbours: ", len(x.splitlines()) - 1)

print("--- Broadcast UDP ---")
#nodes[-1].send_udp_broadcast(1024)
#nodes[-1].send_udp(destination="192.128.64.255", port=5000, size=1024)
#nodes[-1].send_udp(destination=nodes[1].ip_addr, port=5000, size=(2 * 1024)-48)
print("Name: ", nodes[1].node.name)

#x= nodes[-1].node.cmd("route -n")
#x = nodes[-1].node.cmd(f" ping -b -c 1 -s %s %s" % (1024-42, nodes[4].ip_addr))
print(x)

input("Press any key to continue...")

# stop session
session.shutdown()
