docker network prune -f
- NO_PROXY=localhost,127.0.0.1,172.20.0.1,host.docker.internal,172.20.0.0/16
      - no_proxy=localhost,127.0.0.1,172.20.0.1,host.docker.internal,172.20.0.0/16

docker compose -f docker-compose-debug.yml up -d
bash debug_network.sh

docker stop $(docker ps -aq)
docker compose -f docker-compose-debug.yml down

sudo ip link delete br-6fca0d5af4c4
sudo ip link delete br-a58158e9cf35

docker network prune -f

export NO_PROXY=localhost,127.0.0.1,172.20.0.1,host.docker.internal,172.20.0.0/16,172.17.0.0/16
export no_proxy=localhost,127.0.0.1,172.20.0.1,host.docker.internal,172.20.0.0/16,172.17.0.0/16

ip addr | grep 172.20

docker compose -f docker-compose-arx-env.yml down --remove-orphans ???

DEFAULT_FORWARD_POLICY="ACCEPT" в /etc/default/ufw
DEFAULT_INPUT_POLICY="ACCEPT" в /etc/default/ufw

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker network prune -f
sudo ip link delete br-6fca0d5af4c4
sudo ip link delete br-24d6a2cb6f50

alex@alex-IdeaPad-Slim-3-15AMN8:~/source/repos/test-arcium$ bash debug_network.sh
🔍 Начинаем глубокую диагностику сети Arcium...

1. Тест DNS (может ли контейнер разрешать имена?):
Server:         127.0.0.11
Address:        127.0.0.11#53

Non-authoritative answer:
Name:   google.com
Address: 64.233.161.100
Name:   google.com
Address: 64.233.161.101
Name:   google.com
Address: 64.233.161.139
Name:   google.com
Address: 64.233.161.138
Name:   google.com
Address: 64.233.161.102
Name:   google.com
Address: 64.233.161.113
Name:   google.com
Address: 2a00:1450:4010:c05::66
Name:   google.com
Address: 2a00:1450:4010:c05::8a
Name:   google.com
Address: 2a00:1450:4010:c05::71
Name:   google.com
Address: 2a00:1450:4010:c05::8b


2. Тест внешнего соединения (Ping 8.8.8.8):
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=102 time=112 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=102 time=135 ms

--- 8.8.8.8 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 111.598/123.077/134.556/11.479 ms

3. Тест host.docker.internal (видит ли контейнер хост?):
PING host.docker.internal (172.17.0.1) 56(84) bytes of data.
64 bytes from host.docker.internal (172.17.0.1): icmp_seq=1 ttl=64 time=0.116 ms
64 bytes from host.docker.internal (172.17.0.1): icmp_seq=2 ttl=64 time=0.079 ms

--- host.docker.internal ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1022ms
rtt min/avg/max/mdev = 0.079/0.097/0.116/0.018 ms

4. Тест порта Solana RPC (8899) на хосте:
Connection to 172.20.0.1 8899 port [tcp/*] succeeded!

5. Тест P2P связи между контейнерами (100 -> 101):
PING 172.20.0.101 (172.20.0.101) 56(84) bytes of data.
64 bytes from 172.20.0.101: icmp_seq=1 ttl=64 time=0.138 ms
64 bytes from 172.20.0.101: icmp_seq=2 ttl=64 time=0.124 ms

--- 172.20.0.101 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1043ms
rtt min/avg/max/mdev = 0.124/0.131/0.138/0.007 ms

6. Проверка MTU (пакеты не должны дробиться):
PING 8.8.8.8 (8.8.8.8) 1472(1500) bytes of data.
1480 bytes from 8.8.8.8: icmp_seq=1 ttl=102 time=167 ms
1480 bytes from 8.8.8.8: icmp_seq=2 ttl=102 time=190 ms

--- 8.8.8.8 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 166.868/178.231/189.595/11.363 ms

# Заменяем фильтр портов на фильтр по IP нод
sudo tcpdump -i any -s 0 -w full_arx_capture.pcap host 172.20.0.100 or host 172.20.0.101
# -i any: слушать все интерфейсы
# -s 0: захватывать пакет целиком (не обрезать)
# -w traffic_capture.pcap: сохранить в файл для Wireshark
# "port 8899 or port 8900 or port 8001": фильтр, чтобы не записывать лишнее (google и т.д.)
sudo tcpdump -i any -s 0 -w traffic_capture.pcap port 8899 or port 8900 or port 8001