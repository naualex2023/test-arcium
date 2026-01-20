docker network prune -f
- NO_PROXY=localhost,127.0.0.1,172.20.0.1,host.docker.internal,172.20.0.0/16
      - no_proxy=localhost,127.0.0.1,172.20.0.1,host.docker.internal,172.20.0.0/16

docker compose -f docker-compose-debug.yml up -d
bash debug_network.sh