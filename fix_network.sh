#!/bin/bash

# 1. Разрешаем пересылку пакетов на уровне ядра
sudo sysctl -w net.ipv4.ip_forward=1

# 2. Настраиваем UFW (главный виновник в 24.04)
# Разрешаем весь трафик внутри Docker-подсети Arcium
sudo ufw allow from 172.20.0.0/16
sudo ufw allow to 172.20.0.0/16

# Разрешаем форвардинг (маршрутизацию) для этой подсети
sudo ufw route allow in on any from 172.20.0.0/16
sudo ufw route allow out on any to 172.20.0.0/16

# 3. Исправляем конфликт nftables и Docker (Nuclear Option)
# Это принудительно разрешает прохождение пакетов через мост
sudo iptables -P FORWARD ACCEPT

# Добавляем правила в начало цепочки Docker, чтобы они имели приоритет
sudo iptables -I DOCKER-USER -i br-+ -j ACCEPT
sudo iptables -I DOCKER-USER -o br-+ -j ACCEPT

# Если имя моста известно (из вашего прошлого лога это было br-a199...), лучше так:
# sudo iptables -I DOCKER-USER -i br-a1991dd35377 -j ACCEPT

# Разрешаем трафик в UFW (Ubuntu 24.04 это любит)
sudo ufw allow from 172.20.0.0/16
sudo ufw route allow in on br-+ from 172.20.0.0/16

# 4. Перезагружаем Docker, чтобы он пересоздал свои цепочки
sudo systemctl restart docker

echo "✅ Сетевые лимиты сняты. Проверьте диагностику еще раз."