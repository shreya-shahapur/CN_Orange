# SDN-Based Path Tracing Tool

**Course:** UE24CS252B - Computer Networks  
**Author:** Shreya Shahapur (PES1UG24CS442)

## Overview

This project implements an SDN-based Path Tracing Tool using **Mininet** on an Ubuntu virtual machine. It creates a custom network topology and traces the forwarding path between hosts using OpenFlow flow tables.

## Topology

```
  h1 ──┐
       s1 ── s2 ── h3
  h2 ──┘
```

- **Hosts:** h1 (`10.0.0.1`), h2 (`10.0.0.2`), h3 (`10.0.0.3`)
- **Switches:** s1, s2 (OVSBridge in standalone mode — no external controller needed)

## Features

- Builds a custom Mininet topology programmatically
- Displays topology overview (hosts, switches, links)
- Validates full connectivity using `pingall` (0% packet loss)
- Traces the forwarding path between all host pairs by reading OpenFlow flow tables
- Works without an external SDN controller (uses OVSBridge standalone mode)

## Requirements

- Ubuntu (tested on Ubuntu VM)
- [Mininet](http://mininet.org/) installed
- Open vSwitch (`ovs-ofctl` available)

```bash
sudo apt-get install mininet openvswitch-switch
```

## Usage

Run the script with root privileges (required by Mininet):

```bash
sudo python3 path_tracer.py
```

## Sample Output

```
=======================================================
  TOPOLOGY OVERVIEW
=======================================================

  Hosts:
    h1  IP: 10.0.0.1  MAC: ...
    h2  IP: 10.0.0.2  MAC: ...
    h3  IP: 10.0.0.3  MAC: ...

  Switches:
    s1
    s2

=======================================================
  VALIDATION: pingall connectivity test
=======================================================
  [PASS] 0% packet loss. All hosts reachable.

=======================================================
  PATH TRACE: h1 --> h3
=======================================================
  Route: h1 --> s1 --> s2 --> h3
```

## How It Works

1. A custom topology is built using Mininet's `Topo` class.
2. The network starts with OVSBridge switches in standalone mode.
3. ICMP pings are triggered between host pairs to install flow rules on the switches.
4. `ovs-ofctl dump-flows` reads the active flow table entries on each switch.
5. The forwarding path is reconstructed by checking which switches have matching rules for the destination IP.
