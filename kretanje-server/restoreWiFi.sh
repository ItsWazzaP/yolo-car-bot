#!/bin/bash

# 1. Заустави и онемогући сервисе
sudo systemctl stop hostapd dnsmasq
sudo systemctl disable hostapd dnsmasq

# 2. Обриши hostapd конфиг
sudo rm -f /etc/hostapd/hostapd.conf

# 3. Врати dnsmasq.conf из backup-a
sudo mv /etc/dnsmasq.conf.backup /etc/dnsmasq.conf 2>/dev/null || echo "dnsmasq.conf backup not found."

# 4. Врати dhcpcd.conf из backup-a
sudo cp /etc/dhcpcd.conf.backup /etc/dhcpcd.conf

# 5. Врати wpa_supplicant.conf из backup-a (ако постоји)
sudo cp /etc/wpa_supplicant/wpa_supplicant.conf.backup /etc/wpa_supplicant/wpa_supplicant.conf 2>/dev/null || echo "wpa_supplicant.conf backup not found."

# 6. Рестартуј сервисе
sudo service dhcpcd restart
sudo systemctl restart dnsmasq

# 7. Обриши iptables правила
sudo iptables -t nat -F
sudo iptables-save | sudo tee /etc/iptables.ipv4.nat > /dev/null

# 8. Рестартуј RPi за потпуно враћање
echo "Рестартујте уређај да би промене ступиле на снагу: sudo reboot"
