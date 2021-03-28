from core.emulator.data import NodeOptions, IpPrefixes, InterfaceData, LinkOptions
from core.emulator.session import Session
from core.nodes.base import CoreNode
from core.nodes.network import WlanNode


class NodeWrapper:

    # CORE session this node is a part of
    session: Session

    # CORE node that is part of the simulation session
    node: CoreNode

    # Options used to create the node
    options: NodeOptions

    # IP address of the interface from this node to the WLAN
    ip_addr: str

    # Interface from this node to the WLAN
    interface: InterfaceData

    # WLAN this node is connected to
    wlan: WlanNode

    def __init__(self, session: Session):
        self.session = session

    # Create a node and it to the network with OSPF enabled by default
    def add_node(self, x: int, y: int, node_type: CoreNode = CoreNode, node_model: str = "router", ospf_enabled: bool = True):
        options = NodeOptions(x=x, y=y, model=node_model)
        self.options = options
        self.node = self.session.add_node(CoreNode, options=options)

        if ospf_enabled:
            self.node.services.append(self.session.service_manager.get_service("OSPFv2"))

        return self

    # Create a link between this node and the WLAN with the specified link options
    def link_wlan(self, ip: IpPrefixes, wlan: WlanNode, link_options: LinkOptions = LinkOptions()):
        self.interface = ip.create_iface(self.node)
        self.ip_addr = str(self.interface.ip4)
        self.session.add_link(self.node.id, wlan.id, self.interface, options=link_options)
        return self

    def start_ospf(self):
        self.session.services.boot_services(self.node)
        return self
