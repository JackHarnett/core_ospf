
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
    def start_services(self):
        self.session.services.boot_services(self.node)
        return self

    # Read the captures packets from the specified interface.
    # NB: stored in a mounter folder, so easier to open using WireShark locally
    def read_capture(self, iface: str = "eth0"):
        path = "/".join([self.session.session_dir, self.node.name + ".conf", "%s.%s.pcap" % (self.node.name, iface)])
        output = self.node.cmd("tcpdump -r %s" % path)
        print("TCP Dump:", output)

    def listen(self, port: int):
        self.node.cmd("mgen port %i output log.drc" % port, wait=False)

    def send_udp(self, destination: str, size: int, port: int = 5000):
        cmd_str = 'mgen event "ON 1 UDP SRC %s DST %s/%i PERIODIC [0.2 %i] count 1"' % (port, destination, port, size)
        print(cmd_str)
        output = self.node.cmd(cmd_str, wait=True)
        print("Sending to ", destination)
        print(output)

    def send_udp_node(self, node, size: int):
        return self.send_udp(node.ip_addr, size=size)

    def send_udp_broadcast(self, size: int):
        return self.send_udp("225.0.0.5", size=size)


