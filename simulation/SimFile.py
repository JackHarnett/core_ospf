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

for x in range(10):
    nodes.append(NodeWrapper(session).add_node(x=50 + 100 * x, y=20 + 100 * x).link_wlan(ip_prefixes, wlan))

session.instantiate()
print("------ Starting Session ------")

time.sleep(10)

x = nodes[-1].node.cmd(f"vtysh -c 'show ip ospf neighbor'")
print("\n--- Neighbours --- \n", x)
print("\n Number of neighbours: ", len(x.splitlines()) - 1)


x = nodes[-1].node.cmd(f" ping -c 5 %s" % nodes[2].ip_addr)
print("\n --- Ping [%s] \n %s --- \n %s" % (nodes[2].node.name, nodes[2].ip_addr, x))

print("---- Read Capture -----")
nodes[2].read_capture()

print("------ Adding new node ------")

nodes.append(NodeWrapper(session).add_node(x=50 + 500, y=500).link_wlan(ip_prefixes, wlan))

print("------ Waiting for convergence ------")

time.sleep(10)

x = nodes[-1].node.cmd(f"vtysh -c 'show ip ospf neighbor'")
print("\n--- Neighbours --- \n", x)
print("\n Number of neighbours: ", len(x.splitlines()) - 1)

x = nodes[-1].node.cmd(f" ping -c 5 %s" % nodes[2].ip_addr)
print("\n --- Ping [%s] \n %s --- \n %s" % (nodes[2].node.name, nodes[2].ip_addr, x))

print("---- Read Capture -----")
nodes[2].read_capture()

input("Enter")

# stop session
session.shutdown()
