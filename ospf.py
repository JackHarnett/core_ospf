# required imports
import time

from core.emulator.coreemu import CoreEmu
from core.emulator.data import IpPrefixes, NodeOptions, LinkOptions
from core.emulator.enumerations import EventTypes
from core.location.mobility import BasicRangeModel
from core.nodes.base import CoreNode
from core.nodes.network import WlanNode

config = """
router ospf6
    interface eth0 area 0
"""

# ip nerator for example
ip_prefixes = IpPrefixes(ip4_prefix="10.0.0.0/24")

# create emulator instance for creating sessions and utility methods
coreemu = CoreEmu()
session = coreemu.create_session()

zebra_service = session.service_manager.get_service("zebra")
ospf_service = session.service_manager.get_service("OSPFv3")

# must be in configuration state for nodes to start, when using "node_add" below
session.set_state(EventTypes.CONFIGURATION_STATE)

# create wlan
options = NodeOptions(x=200, y=200)
wlan = session.add_node(WlanNode, options=options)

# create nodes
options = NodeOptions(model="router", x=100, y=100)
n1 = session.add_node(CoreNode, options=options)
n1.services.append(ospf_service)

options = NodeOptions(model="router", x=300, y=100)
n2 = session.add_node(CoreNode, options=options)
n1.services.append(ospf_service)

# configuring wlan
session.mobility.set_model_config(
    wlan.id,
    BasicRangeModel.name,
    {
        "range": "280",
        "bandwidth": "55000000",
        "delay": "6000",
        "jitter": "5",
        "error": "5",
    },
)

# link nodes to wlan
iface1 = ip_prefixes.create_iface(n1)
session.add_link(n1.id, wlan.id, iface1)
iface1 = ip_prefixes.create_iface(n2)
session.add_link(n2.id, wlan.id, iface1)

options = LinkOptions(delay=100, bandwidth=50_000_000, dup=5, loss=5.5, jitter=0)

iface1 = ip_prefixes.create_iface(n1)
iface2 = ip_prefixes.create_iface(n2)

print("Iface1", iface1.ip4)
print("Iface2", iface2.ip4)

session.add_link(n1.id, n2.id, iface1, iface2)

# start session/usr/local/
session.services.boot_services(n1)
session.services.boot_services(n2)
session.instantiate()


def writeConfig(n):#
    n.cmd(shell=True, args="mkdir -p /etc/quagga/")
    print("Write", n.cmd(shell=True, args="echo '%s' >> /etc/quagga/ospf6d.conf" % config))


def readConfig(n):
    print("Config", n.cmd("cat /etc/quagga/ospf6d.conf"))

time.sleep(2)

writeConfig(n1)
#readConfig(n1)

x = n1.cmd(shell=True, args="pidof ospf6d")
print("OSPF", x)#

x = n1.cmd(shell=True, args="ospf6d -d")
print("OSPF", x)#


x = n2.cmd(shell=True, args="ospf6d -d")
print("OSPF", x)#

time.sleep(20)

x = n1.cmd(f"vtysh -c 'show ip ospf neighbor'")
print("Neighbours:", x)#

x = n1.cmd("ls /usr/local/etc/quagga/")
print("Files", x)

x = n1.cmd(f"route -n")
print(x)#

# do whatever you like here
#input("press enter to shutdownnnn")

# stop session
session.shutdown()