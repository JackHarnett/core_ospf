from pipes import Template

from core.emulator.data import NodeOptions, IpPrefixes, InterfaceData, LinkOptions
from core.emulator.session import Session
from core.nodes.base import CoreNode
from core.nodes.network import WlanNode
from core.errors import CoreCommandError


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
        self.node = self.session.add_node(CoreNode, options=options)  # add the node to the session

        self.node.services.append(self.session.service_manager.get_service("pcap"))  # add the packet capture service

        if ospf_enabled:
            self.node.services.append(self.session.service_manager.get_service("OSPFv2"))  # add OSPF

        return self

    # Create a link between this node and the WLAN with the specified link options
    def link_wlan(self, ip: IpPrefixes, wlan: WlanNode, link_options: LinkOptions = LinkOptions()):
        self.interface = ip.create_iface(self.node)  # create an IP link
        self.ip_addr = str(self.interface.ip4)  # store the IPv4 address for future use
        self.session.add_link(self.node.id, wlan.id, self.interface, options=link_options)  # link the node and WLAN
        return self

    # Boot all enabled services on the node (eg OSPF) after the session has already been initiated
    def start_ospf(self):
        self.session.services.boot_services(self.node)
        self.session.services.get_service(self.node.id, "pcap")
        return self

    def read_capture(self, iface: str = "eth0"""):
        path = "/".join([self.session.session_dir, self.node.name + ".conf", "%s.%s.pcap" % (self.node.name, iface)])
        file = open(path)
        try:
            out = file.read()
            print(out)
        except:
            print()
