#!/bin/bash

# ==============================================================================
# Arcium Network Environment Setup & Fix Script
# Target System: Ubuntu 24.04 with Docker and active VPN
# Purpose: Clean up conflicting bridges and establish a stable 172.20.x.x network
# ==============================================================================

echo "🚀 Starting Arcium Network Environment Cleanup..."

# 1. STOP AND REMOVE ALL ACTIVE CONTAINERS
# This ensures no containers are holding locks on network namespaces or IDs.
echo "⏹ Stopping and removing all containers..."
docker stop $(docker ps -aq) 2>/dev/null
docker rm $(docker ps -aq) 2>/dev/null

# 2. BRING DOWN COMPOSE PROJECTS
# Ensures that network definitions are removed from the Docker daemon.
echo "📉 Cleaning up docker-compose projects..."
docker compose -f docker-compose-debug.yml down --remove-orphans 2>/dev/null
docker compose -f docker-compose-arx-env.yml down --remove-orphans 2>/dev/null

# 3. DELETE CONFLICTING BRIDGE INTERFACES
# Ubuntu 24.04 often leaves "ghost" bridges (br-xxxx) that overlap subnets.
# We remove the specific IDs identified in the logs.
echo "🛡 Deleting conflicting network bridges..."
sudo ip link delete br-6fca0d5af4c4 2>/dev/null
sudo ip link delete br-1c7585f252f1 2>/dev/null
sudo ip link delete br-a58158e9cf35 2>/dev/null

# 4. PRUNE DOCKER NETWORKS
# Removes all unreferenced networks to prevent "Pool overlaps" errors.
echo "🧹 Pruning Docker networks..."
docker network prune -f

# 5. CONFIGURE SYSTEM POLICIES (UFW/Forwarding)
# Necessary for Ubuntu 24.04 to allow traffic to flow between Docker and Host.
echo "🔧 Setting system forwarding policies..."
sudo sysctl -w net.ipv4.ip_forward=1
# Ensure /etc/default/ufw has DEFAULT_FORWARD_POLICY="ACCEPT" manually
# or apply it via iptables for the current session:
sudo iptables -P FORWARD ACCEPT

# 6. SET PROXY EXEMPTIONS
# Prevents the VPN/System proxy from intercepting internal Arcium traffic.
echo "🌐 Exporting NO_PROXY settings..."
export NO_PROXY=localhost,127.0.0.1,172.20.0.1,host.docker.internal,172.20.0.0/16,172.17.0.0/16
export no_proxy=localhost,127.0.0.1,172.20.0.1,host.docker.internal,172.20.0.0/16,172.17.0.0/16

# 7. START THE ENVIRONMENT
echo "🏗 Starting Arcium Debug Environment..."
docker compose -f docker-compose-debug.yml up -d

# 8. RUN DIAGNOSTICS
echo "🔍 Running debug_network.sh..."
bash debug_network.sh

# ==============================================================================
# EXPECTED SUCCESS RESULTS (from successful diagnostic run):
# 1. DNS: google.com resolves (64.233.161.x)
# 2. External: Ping 8.8.8.8 -> 0% packet loss
# 3. Host: Ping 172.17.0.1 -> 0% packet loss (host.docker.internal)
# 4. RPC: Connection to 172.20.0.1 8899 succeeded!
# 5. P2P: Ping 172.20.0.101 -> 0% packet loss
# 6. MTU: Ping 8.8.8.8 (1472 bytes) -> 0% packet loss (Safe for VPN)
# ==============================================================================

echo "✅ Environment is ready for Arcium nodes."