#!/bin/bash

# 1. Инсталирај потребне пакете
sudo apt update
sudo apt install -y hostapd dnsmasq

# 2. Заустави сервисе (привремено)
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# 3. Подеси статичку IP за интерфејс (нпр. wlan0)
sudo tee -a /etc/dhcpcd.conf > /dev/null <<EOL
interface wlan0
    static ip_address=192.168.42.1/24
    nohook wpa_supplicant
EOL

# 4. Рестартуј dhcpcd
sudo service dhcpcd restart

# 5. Подеси hostapd (хотспот)
sudo tee /etc/hostapd/hostapd.conf > /dev/null <<EOL
interface=wlan0
driver=nl80211
ssid=teslapoint
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=tesla1234
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOL

# 6. Подеси hostapd да користи наш конфиг
sudo sed -i 's/#DAEMON_CONF=""/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/g' /etc/default/hostapd

# 7. Подеси dnsmasq (DHCP)
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.backup
sudo tee /etc/dnsmasq.conf > /dev/null <<EOL
interface=wlan0
dhcp-range=192.168.42.10,192.168.42.40,255.255.255.0,24h
EOL

# 8. Рестартуј сервисе
sudo systemctl start dnsmasq
sudo systemctl start hostapd
sudo systemctl enable dnsmasq
sudo systemctl enable hostapd

# 9. Омогући IP форвардинг и NAT
sudo sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g' /etc/sysctl.conf
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables-save | sudo tee /etc/iptables.ipv4.nat > /dev/null

echo "Хотспот 'teslapoint' је подешен! Лозинка: tesla1234"
