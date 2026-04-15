#!/usr/bin/env python3
"""
SDN-Based Path Tracing Tool
Course: Computer Networks
Uses OVSBridge (standalone mode) - NO external controller needed.
"""

from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import subprocess
import time

# ─────────────────────────────────────────────
# Topology:
#   h1 ──┐
#        s1 ── s2 ── h3
#   h2 ──┘
# ─────────────────────────────────────────────
class CustomTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        h1 = self.addHost('h1', ip='10.0.0.1/8')
        h2 = self.addHost('h2', ip='10.0.0.2/8')
        h3 = self.addHost('h3', ip='10.0.0.3/8')

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(s1, s2)
        self.addLink(h3, s2)

def get_flow_rules(switch_name):
    try:
        result = subprocess.check_output(
            ['ovs-ofctl', 'dump-flows', switch_name],
            stderr=subprocess.STDOUT
        ).decode('utf-8')
        return result
    except Exception:
        return ""

def display_topology(net):
    info("\n" + "="*55 + "\n")
    info("  TOPOLOGY OVERVIEW\n")
    info("="*55 + "\n\n")
    info("  Hosts:\n")
    for host in net.hosts:
        info("    {}  IP: {}  MAC: {}\n".format(host.name, host.IP(), host.MAC()))
    info("\n  Switches:\n")
    for sw in net.switches:
        info("    {}\n".format(sw.name))
    info("\n  Links:\n")
    for link in net.links:
        i1 = link.intf1
        i2 = link.intf2
        info("    {}:{} <--> {}:{}\n".format(
            i1.node.name, i1.name, i2.node.name, i2.name))
    info("\n")

def validate_connectivity(net):
    info("\n" + "="*55 + "\n")
    info("  VALIDATION: pingall connectivity test\n")
    info("="*55 + "\n\n")
    loss = net.pingAll()
    if loss == 0.0:
        info("\n  [PASS] 0%% packet loss. All hosts reachable.\n")
    else:
        info("\n  [FAIL] Packet loss: {}%%\n".format(loss))
    return loss

def trace_path(net, src_name, dst_name):
    info("\n" + "="*55 + "\n")
    info("  PATH TRACE: {} --> {}\n".format(src_name, dst_name))
    info("="*55 + "\n\n")

    src = net.get(src_name)
    dst = net.get(dst_name)
    dst_ip = dst.IP()

    info("  Source      : {} ({})\n".format(src_name, src.IP()))
    info("  Destination : {} ({})\n\n".format(dst_name, dst_ip))

    info("  [1] Sending ping to install flow rules...\n")
    src.cmd('ping -c 3 {} > /dev/null 2>&1'.format(dst_ip))
    time.sleep(1)

    info("  [2] Flow rules on each switch:\n\n")
    for sw in net.switches:
        flows = get_flow_rules(sw.name)
        info("  --- {} ---\n".format(sw.name))
        printed = False
        for line in flows.splitlines():
            if 'actions=' in line:
                info("    {}\n".format(line.strip()))
                printed = True
        if not printed:
            info("    (no rules yet)\n")
        info("\n")

    info("  [3] Forwarding Path:\n")
    path = [src_name]
    for sw in net.switches:
        flows = get_flow_rules(sw.name)
        if dst_ip in flows and 'output' in flows:
            path.append(sw.name)
    path.append(dst_name)
    info("  Route: {}\n\n".format(" --> ".join(path)))

def run():
    setLogLevel('info')

    info("\n*** Building topology (no external controller needed)...\n")
    topo = CustomTopo()

    # OVSBridge works in standalone mode - no controller required
    net = Mininet(topo=topo, switch=OVSBridge, controller=None)

    info("*** Starting network...\n")
    net.start()
    time.sleep(2)

    display_topology(net)
    validate_connectivity(net)

    info("\n*** Warming up flow tables...\n")
    for h in net.hosts:
        for g in net.hosts:
            if h != g:
                h.cmd('ping -c 1 {} > /dev/null 2>&1'.format(g.IP()))
    time.sleep(2)

    trace_path(net, 'h1', 'h2')
    trace_path(net, 'h1', 'h3')
    trace_path(net, 'h2', 'h3')

    info("\n*** Entering CLI. Type 'exit' to quit.\n\n")
    CLI(net)

    net.stop()

if __name__ == '__main__':
    run()
