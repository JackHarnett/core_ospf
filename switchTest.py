# required imports

import netaddr, dataclasses, fabric, lxml, pyproj
from core.emulator.coreemu import CoreEmu
from core.emulator.data import IpPrefixes, NodeOptions
from core.emulator.enumerations import EventTypes
from core.nodes.base import CoreNode
from core.nodes.network import SwitchNode


# ip nerator for example
ip_prefixes = IpPrefixes(ip4_prefix="10.0.0.0/24")

# create emulator instance for creating sessions and utility methods
coreemu = CoreEmu()
session = coreemu.create_session()

print(session)

# must be in configuration state for nodes to start, when using "node_add" below
session.set_state(EventTypes.CONFIGURATION_STATE)

# create switch
options = NodeOptions(x=200, y=200)
switch = session.add_node(SwitchNode, options=options)

# create nodes
options = NodeOptions(x=100, y=100)
n1 = session.add_node(CoreNode, options=options)
options = NodeOptions(x=300, y=100)
n2 = session.add_node(CoreNode, options=options)

# link nodes to switch
iface1 = ip_prefixes.create_iface(n1)
session.add_link(n1.id, switch.id, iface1)
iface1 = ip_prefixes.create_iface(n2)
session.add_link(n2.id, switch.id, iface1)

# start session
session.instantiate()

# do whatever you like here
input("press enter to shutdown")

# stop session
session.shutdown()
