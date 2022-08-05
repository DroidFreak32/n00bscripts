# Description
These are my notes for future reference on how I setup my Raspberry Pi for my specific need at the time.

## My needs
I want my Pi to act as

1. A PiHole to block ads
2. A recursive DNS resolver using unbound
3. A WireGuard VPN to access my home network
4. A WireGuard VPN "Relay" to be able to share a Single VPN connection over multiple client devices that are also WireGuard Peers
5. Manage VPN Stuff easily using PiVPN
6. Extend all these to support travelling (i.e. Using a 4g Dongle over USB)
    - This is where bridging USB and NIC comes into picture.
    - Some dongles do not allow changing the LAN subnet, so unfortunately DHCP will be required to setup the Internet facing interfaces.
7. Use it as a wireless AP to bypass dongle restrictions
~~8. Use IPv6-in-IPv4 Relay (route48) for IPV6 support~~  
Let's get started.
___
### Setting up a bridge interface configs for `systemd-networkd`
Purpose: 
When using broadband, we use the gigabit NIC `eth0` however if we are to use a USB dongle, rPi will create eth1.
Settings up a "universal" bridge interface `br0` to combine both `eth0` and `eth1` will make the rest of our configuration easy, since we can just point them to `br0`

1) Creating the bridge dev `br0`:
```
root@horcrux-pi:/etc/systemd/network # cat 05-br0.netdev
[NetDev]
Name=br0
Kind=bridge
```
2) Assigning `eth0` and `eth1` to `br0`
```
root@horcrux-pi:/etc/systemd/network # cat 06-br0-eth0.network
[Match]
Name=eth0
[Network]
Bridge=br0

root@horcrux-pi:/etc/systemd/network # cat 07-br0-eth1.network
[Match]
Name=eth1
[Network]
Bridge=br0
```
3) Configureing `br0` with DHCP and setting the Master MAC
```
[Match]
Name=br0

[Network]
DHCP=yes
DNS=1.1.1.1

[Link]
MACAddress=e4:5f:01:95:ce:dd
```
Note: DNS is set here since rPi does not preserve time when off, leading to issues with `unbound`. We need this to make the Pi sync with an NTP on boot.

4) Disable DHCP on the pNICs in `/etc/dhcpcd.conf`
```
denyinterfaces eth0 eth1
```
5) Reboot & verify br0 is up and eth0 doesnt have a DHCP lease
```
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq master br0 state UP group default qlen 1000
    link/ether <MAC> brd ff:ff:ff:ff:ff:ff
3: br0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether <MAC> brd ff:ff:ff:ff:ff:ff
    inet <IP/MASK> brd 192.168.5.255 scope global br0
```

### Setting up a wireless AP
1) Create `/etc/hostapd/hostapd.conf`
```
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
auth_algs=1
beacon_int=100

ssid=raspi-webgui
wpa_passphrase=hackmenot

# Change this to your country
country_code=US

interface=wlan0
# Uncomment if you want to use upstream router/dongle to directly handle clients
#bridge=br0
driver=nl80211

wpa=2
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP

macaddr_acl=0

logger_syslog=0
logger_syslog_level=4
logger_stdout=-1
logger_stdout_level=0

# Change this to 'a' to use 802.11ac
hw_mode=g
wmm_enabled=1

# N
ieee80211n=1
require_ht=1
# uncomment to use 802.11ac
#ht_capab=[MAX-AMSDU-3839][HT40+][HT40-][SHORT-GI-20][SHORT-GI-40][DSSS_CCK-40]
#ht_capab=[MAX-AMSDU-3839][HT40+][HT40-][SHORT-GI-20][DSSS_CCK-40]
# Comment to use AC channels
channel=11

# AC (Uncomment to use 802.11ac)
#ieee80211ac=1
#require_vht=1
#ieee80211d=0
#ieee80211h=0
#vht_capab=[MAX-AMSDU-3839][SHORT-GI-80]
#vht_oper_chwidth=1
#channel=36
#vht_oper_centr_freq_seg0_idx=42

ignore_broadcast_ssid=0
```
2) Unmask and start hostapd service
`systemctl unmask hostapd && systemctl start hostapd`

This should be enough, <ins>**however if you did not set `bridge=br0`**</ins> you'll need to setup additional configs 

### Wireless AP: Optional Steps if not using br0

We'll need to setup NAT rules, DHCP server etc
1) Install `iptables` for wlan forwarding  
  `sudo apt install iptables-persistent iptables-netflow-dkms iptables nftables`
2) Set a static IP for `wlan0` in `/etc/dhcpcd.conf`
```
interface wlan0
  static ip_address=192.168.4.254/24
  nohook wpa_supplicant
```
3) Add the following dnamasq config for the wlan AP
```
no-dhcp-interface=eth1
no-dhcp-interface=eth0
no-dhcp-interface=br0
interface=wlan0 # Listening interface
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
                # Pool of IP addresses served via DHCP
domain=wlan     # Local wireless DNS domain
local=/wlan/
address=/gw.wlan/192.168.4.254
                # Alias for this router
dhcp-leasefile=/etc/pihole/dhcp.leases
dhcp-rapid-commit

#quiet-dhcp6
#enable-ra
#dhcp-option=option6:dns-server,[::]
#dhcp-range=::,constructor:wlan0,ra-names,ra-stateless,64

## This will allow you to have pihole listen on specific interfaces other than what is listed in the webui
## the current pihole options are one, or all. this let's you be a bit more precise.
interface=br0
```
4) Set the following iptables rules to forward traffic from wlan0 to our br0
`/etc/iptables/rules.v4:`
```
-A POSTROUTING -s 192.168.4.0/24 -o br0 -m comment --comment "Dongle AP Fwd Support" -j MASQUERADE
```
Now you should be ready to have your Pi act like an AP and also use its inbuild PiHole to block ads

### PiHole + Unbound setup

1) Install PiHole following the docs, choose br0 as the interface and Skip setting Static IP  
2) Setup unbound: https://docs.pi-hole.net/guides/dns/unbound/  
3) Disable the unbound-resolvconf service
4) Create this systemd timer to delay unbound's resolvconf service:
```
$ cat /etc/systemd/system/unbound-resolvconf.timer
[Timer]
OnBootSec=1min

[Install]
WantedBy=timers.target
```
5) Enable timer  `sudo systemctl enable unbound-resolvconf.timer`

