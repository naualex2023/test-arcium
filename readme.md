Arcium Network Sandbox & Troubleshooting Guide

This repository contains tools and configurations to deploy, diagnose, and fix the networking environment for Arcium nodes, specifically optimized for Ubuntu 24.04 users operating behind a VPN.
📌 Overview

Arcium nodes require a complex multi-layered network setup:

    P2P Communication: High-speed internal traffic between nodes (Port 8001).

    Solana RPC/PubSub: Reliable connections to the blockchain (Ports 8899/8900).

    Cross-Bridge Routing: Access to the host machine via host.docker.internal.

🚀 Quick Start: Environment Setup

To ensure a clean deployment without "Pool overlaps" or "Network not found" errors, use the provided setup script.
1. Networking Fix & Cleanup (setup_env.sh)

This script performs a deep cleanup of the Docker network stack and applies the necessary routing policies.
Bash

#!/bin/bash
# Arcium Network Environment Setup

# Stop and remove lingering containers to release network IDs
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

# Cleanup compose projects and prune networks
docker compose -f docker-compose-debug.yml down --remove-orphans
docker network prune -f

# Delete conflicting ghost bridges (common in Ubuntu 24.04)
sudo ip link delete br-6fca0d5af4c4 2>/dev/null
sudo ip link delete br-1c7585f252f1 2>/dev/null

# Apply forwarding policies and bypass proxy for local traffic
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -P FORWARD ACCEPT
export NO_PROXY=localhost,127.0.0.1,172.20.0.1,host.docker.internal,172.20.0.0/16

🔍 Diagnostics & Validation

Before running the full node environment, validate the network integrity using the debug_network.sh script.
Successful Diagnostic Baseline:

A healthy environment should produce the following results:
Test	Target	Expected Result	Status
DNS	google.com	Successful resolution	✅
Internet	8.8.8.8	0% packet loss	✅
Gateway	172.17.0.1	Reachable (host.docker.internal)	✅
Solana RPC	172.20.0.1:8899	Connection succeeded!	✅
P2P	172.20.0.101	Internal nodes reachable	✅
MTU	1472 bytes	No fragmentation (VPN Friendly)	✅
🛠 Troubleshooting Known Issues
1. "Pool Overlaps" Error

Cause: Docker tries to create 172.20.0.0/16 while a ghost bridge or another project is using it. Fix: Run docker network prune -f and manually delete bridges using sudo ip link delete <bridge_name>.