# n00bscripts & configs

### Zephyrus G15 2021 Linux Mods

#### Enable SysRq support

Credits: [ASUS-Linux](https://asus-linux.org/faq/#mic-mute-doesn-t-work) & [foell](https://www.foell.org/justin/remapping-keyboard-keys-in-ubuntu-with-udev-evdev)

1) **Note down the keyboard IDs using `ls -l /dev/input/by-id/usb-ASUSTeK*`**
 ```bash
 ❯ ls -al /dev/input/by-id/usb-ASUSTeK*
lrwxrwxrwx 1 root root 9 Sep 10 22:32 /dev/input/by-id/usb-ASUSTeK_Computer_Inc._N-KEY_Device-event-if00 -> ../event7
lrwxrwxrwx 1 root root 9 Sep 10 22:32 /dev/input/by-id/usb-ASUSTeK_Computer_Inc._N-KEY_Device-if02-event-kbd -> ../event6
```
The one ending with `if02-event-kbd` corresponds to the generic keys (qwerty, fn1-fn12, esc, delete etc).  
Whereas the other one corresponds to the secondary actions (VOL_UP, VOL_DOWN, MIC_MUTE, all fn+<key> combos)  

It is on you to decide which key you'd like to remap to SysRq.  

In my case, I will choose the `menu` key (`fn+RightCtrl`) as SysRq <-> `event7` above


2) **Get the details of `Asus Keyboard` using `evemu-describe`. You may see multiple entries but for this step any one will work, for ex below it is event`6`**

```bash
❯ evemu-describe
Available devices:
/dev/input/event0:      Lid Switch
/dev/input/event1:      Power Button
/dev/input/event2:      Sleep Button
/dev/input/event3:      Video Bus
/dev/input/event4:      Asus Wireless Radio Control
/dev/input/event5:      LogiOps Virtual Input
/dev/input/event6:      Asus Keyboard
/dev/input/event7:      Asus Keyboard
...
Select the device event number [0-26]: 6
```

3) **Enter the ID in the prompt and take a note of the Properties lines:**

```bash
...
# Properties:
N: Asus Keyboard
I: 0003 0b05 19b6 0110
...
```
The first three sections (in ALL CAPS) will be required later: `0003 0B05 19B6`  
These are the `bus-id` `vendor-id` and `product-id` respectively.


4) **Next, choose a key to remap and gather its KeyCode and `ScanCode` info.**
 - Since I am using `fn+RightCtrl` I'll need to scan its key/scan code by listening on `event6`.
 - If you want to choose another key (ex, the `AURA` key under `f4`) you'll have to listen to its events `event7`
 - Use `evtest /dev/input/by-id/usb-ASUSTeK....` to start listening to the key/scan codes. The output in my case:
```bash
Properties:
Testing ... (interrupt to exit)
Event: time 1662833525.476492, type 4 (EV_MSC), code 4 (MSC_SCAN), value 70065
Event: time 1662833525.476492, type 1 (EV_KEY), code 127 (KEY_COMPOSE), value 1
Event: time 1662833525.476492, -------------- SYN_REPORT ------------
Event: time 1662833525.577281, type 4 (EV_MSC), code 4 (MSC_SCAN), value 70065
Event: time 1662833525.577281, type 1 (EV_KEY), code 127 (KEY_COMPOSE), value 0
Event: time 1662833525.577281, -------------- SYN_REPORT ------------
```
From the output above, the `ScanCode` is `70065` and `KeyCode` is [`KEY_COMPOSE`](https://github.com/torvalds/linux/blob/v5.19/include/uapi/linux/input-event-codes.h#L204)  

If using `AURA` key for ex, you'll have to run `evtest` on `usb-ASUSTeK..event-if00` and the output would be something like
```bash
Testing ... (interrupt to exit)
Event: time 1662834149.898966, type 4 (EV_MSC), code 4 (MSC_SCAN), value ff3100b3
Event: time 1662834149.898966, type 1 (EV_KEY), code 202 (KEY_PROG3), value 1
Event: time 1662834149.898966, -------------- SYN_REPORT ------------
```
So in this case the `ScanCode` is `ff3100b3`, currently mapped to [`KEY_PROG3`](https://github.com/torvalds/linux/blob/v5.19/include/uapi/linux/input-event-codes.h#L279)


5) **Create a udev `.hwdb` file to remap keys**
 - Create a new file in `/etc/udev/hwdb.d/` ending with `.hwdb` with the following contents
 - Substitute with your `KEYBOARD_KEY_<SCANCODE>`

```
❯ cat /etc/udev/hwdb.d/90-nkey.hwdb
# Input device ID: bus 0003 vendor 0B05 product 19B6
# evdev:input:b<bus_id>v<vendor_id>p<product_id>e<version_id>-<modalias>
evdev:input:b0003v0B05p19B6*
 KEYBOARD_KEY_70065=sysrq # force sysrq to fn+rightctrl
```
`sysrq` can be replaced with any keycode supported in this list: https://github.com/torvalds/linux/blob/v5.19/include/uapi/linux/input-event-codes.h

---
## Pi-Hole setup

### Description
These are my notes for future reference on how I setup my Raspberry Pi for my specific need at the time.

#### My needs
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
# Generated by iptables-save v1.8.7 on Fri Aug  5 20:34:31 2022
*nat
:PREROUTING ACCEPT [10731:800057]
:INPUT ACCEPT [9895:546267]
:OUTPUT ACCEPT [386:262218]
:POSTROUTING ACCEPT [386:262218]
-A POSTROUTING -s 192.168.4.0/24 -o br0 -m comment --comment "Dongle AP Fwd Support" -j MASQUERADE
COMMIT
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

6) Remove redundant configs from Pihole as per [this](https://www.reddit.com/r/pihole/comments/d9j1z6/unbound_as_recursive_dns_server_slow_performance/f1jnuq1/) reddit post:
```
# /etc/unbound/unbound.conf.d/pi-hole.conf
    cache-min-ttl: 0
    serve-expired: yes
# /etc/dnsmasq.d/01-pihole.conf
cache-size=0
```


## Pi-Hole modifications
### <s>Restricting access outside LAN
Added the following in `/etc/lighttpd/lighttpd.conf`</s>
```
# Only allow LAN
$HTTP["remoteip"] != "192.168.5.0/16" {
  url.access-deny = ("")
}
```

### Listen on multiple interfaces
Create or edit dnsmasq configs, in my case: `/etc/dnsmasq.d/42-wlan0_ap.conf`
```
## This will allow you to have pihole listen on specific interfaces other than what is listed in the webui
## the current pihole options are one, or all. this let's you be a bit more precise.
interface=br0
interface=wg0
```
### Restrict service access to LAN:
Use `iptables` to block connections outside LAN `/etc/iptables/rules.v4`:
```
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A INPUT -s 192.168.0.0/16 -p tcp -m multiport --dports 22,53,80,443,5900 -m comment --comment "Allows LAN devices to access to known services" -j ACCEPT
-A INPUT -s 192.168.0.0/16 -p udp -m multiport --dports 22,53,80,443,5900 -m comment --comment "Allows LAN devices to access to known services" -j ACCEPT
-A INPUT -p tcp -m multiport --dports 22,53,80,443,5900 -j REJECT --reject-with tcp-reset
COMMIT
```
___
## Load balancing multiple internet connections over a single NIC with help of [dispatch-proxy](https://github.com/alexkirsz/dispatch)
#### My Setup
Home LAN: `192.168.1.0/24`  
ISP Gateway (`RT`): `192.168.1.1/24`  
Raspberry Pi (`RPi`): `192.168.1.2/24` (Static with no default gateway)  
My Laptop (`LPt`): `192.168.1.100/24` (DHCP)  

I have my ISP FTTH router (`RT`) set to PPPoE passthrough mode which lets any one LAN device also send PPP requests.  
This lets me have my Raspberry Pi - connected to `RT`'s LAN at `192.168.1.2` - send PPP requests and have its own PPP connection:
```
<WAN1> <WAN2>
    |    |
    |    `-RT - <PPP Public IP 1>
    |      `-br_lan - 192.168.1.1/24
    |        `-LPt
    |          `-eth0 - 192.168.1.100/24 (default gateway: 192.168.1.1)
    |        `-RPi 
    |          `-eth0 - 192.168.1.2/24 (default gateway: ppp0)
    `------------`-ppp0 - <PPP PUBLIC IP 2>
```
Note: `ppp0` can be any of your internet facing interface (`eth1`/`wlan0` etc)

By design, each network can only have 1 default gateway.  
However, in my case I am able to access the internet from both `RT` and `rPI` which are both under the `192.168.1.0/24` network.
`LPt` by default can only access internet through `RT`

To overcome this, we can make use of a new subnet `192.168.2.0/24` + a new routing table `100` + routing rules to use table `100` for `192.168.2.0/24`.
```
`-LPt
  `-eth0 - 192.168.1.100/24 (default gateway: 192.168.1.1, rt_table=main)
         - 192.168.2.100/24 (default gateway: 192.168.2.2, rt_table=100) *** New subnet ***
`-RPi 
  `-eth0 - 192.168.1.2/24 (default gateway: ppp0)
         - 192.168.2.2/24 (default gateway: ppp0 through NAT) *** New subnet ***
```
First, setup an additional subnet within `RPi` and `LPt` only.
`LPt` & `RPi`:
```
# Add a new address
ncli connection modify Ethernet +ipv4.addresses "192.168.2.100/24"
# Or use: ip addr add "192.168.2.2/24" dev eth0
```
Next, on `LPi` add a default route via `RPi` on a separate routing table `100`
```
# Add additional default routes in separate tables
nmcli connection modify Ethernet +ipv4.routes "0.0.0.0/0 192.168.2.2 table=100"
# ip route add default via 192.168.2.2 table 100
```
Next, create a rule on `LPi` for all packets in `192.168.2.0/24` to use routing table `100`
```
# Add custom routing rules
nmcli connection modify Ethernet +ipv4.routing-rules "priority 100 from 192.168.2.0/24 table 100"
# ip rule from 192.168.2.0/24 table 100 priority 100
```
Next, on `RPi`, we need to `MASQUERADE` all incoming packets from `192.168.2.0/24` to `192.168.1.2` inorder to get out through `ppp0`.
```
sudo iptables -t nat -A POSTROUTING -s 192.168.2.0/24 -o ppp0 -j MASQUERADE
```
With this, we now have 2 separate routes a packet from `LPt` can go through.
The route is decided based on the source IP. `192.168.1.x` goes through `RT` whereas `192.168.2.x` goes through `RPi`
If you now go to https://ipleak.net and run their `Torrent Address detection` you should be seeing 2 Public IPs.
However, not all apps can make use of this. Almost everything will still go out with source address `192.168.1.x`

This is where [dispatch-proxy](https://github.com/alexkirsz/dispatch) comes in.
1. Run `dispatch list`.
```
╔════════╦═══════════════╗
║  eth0  ║ 192.168.1.100 ║
║        ║ 192.168.2.100 ║
╚════════╩═══════════════╝
```
2. Start the proxy `dispatch start 192.168.1.100 192.168.2.100`
3. Run `curl -x socks5h://localhost:1080 ifconfig.me` multiple times to verify your Public IP is changing.
4. On any app/browser that supports SOCKS5 Proxy, use 127.0.0.1:1080

### Additional ideas:
- It may not have to even be on a separate subnet, we could probably just add a new address in existing subnet set a rule just for the new IP
- These rules could be implemented on `RPi` itself and the Proxy exposed to lan. So any device in LAN will be able leverage the speeds just by setting a system-wide proxy.
___


## WireGuard config to "split-tunnel" into a VPN,

Within your VPN-provider's WireGuard config you need to make a couple of changes Inside `[Interface]` Section.  
I named it wg-vpn.conf

```ini
[Interface]
# Prevent WireGuard from creating any routing tables.
# You definitely don't want your existing PiHole users to get access to this VPN
Table = off

# Create a new Routing table specific to clients connecting to VPN
PostUp = ip route add default dev wg-vpn table 1337
PreDown = ip route del default dev wg-vpn table 1337
```

Then you need to create a new WireGuard "bridge" interface config.  
This cannot be your DNS-only/PiHole interface because it would then depend on `wg-vpn` interface to be always up.

I have set up my bridge interface like so:

```ini
[Interface]
Address = <NEW SUBNET (10.10.0.1/24)>
ListenPort = <PORT>
PrivateKey = <NEW PRIVATE KEY>
Table = off

# Start the VPN interface
PreUp = wg-quick up wg-vpn
# Use the VPN interface for all traffic
PostUp = iptables -w -t nat -A POSTROUTING -o wg-vpn -j MASQUERADE ; ip6tables -w -t nat -A POSTROUTING -o wg-vpn -j MASQUERADE

# All packets from this "bridge" should use our custom routing table using the VPN
PostUp = ip rule add from 10.10.0.0/24 lookup 1337
# Make this subnet reachable through this interface for all incoming packets from VPN
PostUp = ip route add 10.10.0.0/24 dev %i table 1337

# Cleanup
PreDown = ip rule del from 10.10.0.0/24 lookup 1337
PostDown = iptables -w -t nat -D POSTROUTING -o wg-vpn -j MASQUERADE; ip6tables -w -t nat -D POSTROUTING -o wg-vpn -j MASQUERADE
PostDown = wg-quick down wg-vpn

# oneplus8t-rushab
[Peer]
PublicKey = <PUB>
PresharedKey = <PSK>
AllowedIPs = 10.10.0.2/32
```
TODO:
- Figure out why the main routing table contains bridge0 route despite Table = off
- Implement Firewall to block anything outside this network
- Figure out fwmask ([tldr](https://datahacker.blog/industry/technology-menu/networking/routes-and-rules/iproute-and-routing-tables))

##### bonus config for *enterprise* VPN:
```ini
[Interface]
PrivateKey = 
Address = hh.hh.hh.1/24,hx:hx:hx:h112::1/112
MTU = 1420
ListenPort = PORT
Table = off

# Use the VPN interface for all traffic
PostUp = iptables -w -t nat -A POSTROUTING -s hh.hh.hh.0/24 -o work_tun -j MASQUERADE ; ip6tables -w -t nat -A POSTROUTING -o work_tun -j MASQUERADE
# Cleanup
PostDown = iptables -w -t nat -D POSTROUTING -s hh.hh.hh.0/24 -o work_tun -j MASQUERADE; ip6tables -w -t nat -D POSTROUTING -o work_tun -j MASQUERADE
####### Interface END #######


### begin Rushab8T-Work ###
[Peer]
PublicKey = 
PresharedKey = 
AllowedIPs = hh.hh.hh.3/32,hx:hx:hx:h112::3/128
### end Rushab8T-Work ###
```
---

## Replace text from files
```bash
perl -pi -w -e 's/<OLD>/<NEW>/g;' <filename>
```
Replace `<OLD>` with the current tag and `<NEW>` with the new one

## Recursively Check for missing/corrupted FLAC files
```bash
grep -a -L -r -E --include="*.flac" "libFLAC|fLaC"
```
## Check for files that weren't properly encoded to OPUS
```bash
# Finds all *.flac files and sends the sorted list to a.txt
find . -name "*.flac" | sort > a.txt

# Using git to commit the file list inorder to do a git diff later. 
git init . ; git add a.txt ; git commit -m "Init"

# Finds all encoded *.opus files, renames the extension to .flac and overwrites a.txt with the new list.
find . -name "*.opus" | sort | sed 's/.opus$/.flac/g;' > a.txt

# The FLAC files which are corrupted are now shown "missing" in the new list (As they couldn't be encoded).
git diff a.txt
```

## Archive SCANS folders from FLAC rips to reduce no. of files.
```bash
export CWD="$PWD"
export array=()
while IFS=  read -r -d $'\0'; do
    array+=("$REPLY")
done < <(find . -type d \( -iname "scan*" -o -iname "*bookl*" \) -print0)
for i in "${array[@]}"
do
        BASEDIRNAME=$(basename "$i")
        PARENTDIRNAME=$(dirname "$i")
        cd "$PARENTDIRNAME"
        rar a "$BASEDIRNAME".rar -m0 -df "$BASEDIRNAME"
        cd "$CWD"
done
```

## Backup the rootfs of Ubuntu 18.04 with Multi-Threaded compression (Requires pxz).
```bash
# This may be useful: https://github.com/azuer88/grub-mkconfig_lib-patch
XZ_OPT=-9 tar -I pxz -cp \
--exclude=/backup.txz.gpg \
--exclude=/proc \
--exclude=/tmp \
--exclude=/mnt \
--exclude=/dev \
--exclude=/sys \
--exclude=/swap.img \
--exclude=/run \
--exclude=/media \
--exclude=/var/log \
--exclude=/var/cache/apt/archives \
--exclude=/usr/src/linux-headers* \
--exclude=/home/*/.gvfs \
--exclude=/home/*/.cache \
--exclude=/home/*/.ccache \
--exclude=/home/*/.local/share/Trash \
--exclude=/home/*/los \
--exclude=/home/*/.gdfuse/*/cache / | gpg -e -r <email id> -o backup.txz.gpg
```

## To extract the backup and install the system:
```bash
gpg --armor  --export-secret-keys <email id> > private.key
gpg --import private.key
gpg -d backup.txz.gpg | tar -xJ

for i in /dev /dev/pts /proc /sys /run; do sudo mount -B $i /mnt$i; done
chroot /mnt
grub-install /dev/sda
```

## Modify Media file timestamps from the names
#### Must be of format IMG-YYYYMMDD-randomtext.jpg"
```bash
for i in "$(cat /sdcard/WAIMAGES.txt)"
do
    TIMESTAMP="$(echo $i | awk -F '-' '{print $2}')";
    touch -c -t "$TIMESTAMP" $i
    ls -l $i
done
```
####  This is for format IMG_20190629_142823_662.jpg used by telegram
```bash
find . -type f -name "*201*" > /sdcard/tg.txt
for i in "$(cat /sdcard/tg.txt)"
do
    TIMESTAMP="$(echo $i | awk -F '_' '{print $2$3$4}')";
    TIMESTAMP="${TIMESTAMP::-4}" # Remove extension
    touch -c -t "${TIMESTAMP:0:12}.${TIMESTAMP:12}" $i
    ls -l $i
done
```


## ADB - recursively scan media from [find result](https://stackoverflow.com/questions/1279953/how-to-execute-the-output-of-a-command-within-the-current-shell)
```bash
find /sdcard/ -type f -iname "*.flac" |sed -e "s|^|am broadcast -a 'android.intent.action.MEDIA_SCANNER_SCAN_FILE' -d file://\"|g;" -e "s|$|\"|g;"| source /dev/stdin
```
```text
Explanation:
1) find /sdcard/ -type f -iname "*.flac" 
 - Prints all the matched files.

2) sed -e "s|^|am broadcast -a 'android.intent.action.MEDIA_SCANNER_SCAN_FILE' 
 - Replaces the start of each `find` result with
 am broadcast -a 'android.intent.action.MEDIA_SCANNER_SCAN_FILE'
 - -d file://\"|g;" Then adds a " at the end of file:// to complete the string as:
 am broadcast -a 'android.intent.action.MEDIA_SCANNER_SCAN_FILE' -d file://"
 
3)  -e "s|$|\"|g;"
 - appends " at the end of the output to close the " in step 2

4) | source /dev/stdin
 - Executes the output as a command
```

## RSync - Sync sdcard & PC, remove deleted items in target
 - Phone to PC
```bash
rsync -av --recursive -P --dry-run -e "ssh -i /data/ssh/ssh_host_rsa_key" /sdcard/ username@IP:~/Android/sdcard --delete
```
 - PC to Phone (Needs root for `/sdcard/Android/obb` )
```bash
rsync -av --recursive -P --dry-run -e  "ssh -i /sdcard/.ssh/id_ed25519" username@IP:~/Android/sdcard/ /sdcard --delete
```


## There are just few simple shell 1-liners I keep forgetting. Hopefully I don't get lazy to update this file after I google the things I need.

#### `find` and empty the contents of files:

```bash
find . -type f -exec truncate -s 0 {} \;
```
---
#### Take each line from a text file as an input (useful if you redirect the o/p of a find result to a file).
 - #### *This MAY NOT escape special characters!*
```bash
while read p; do ls -al "$p" ; done < list.txt
```
---
#### [Build AOSP without getting bullied by metalava](https://sx.ix5.org/info/building-android/#fnref:2)
 - ##### *NOTE: Does not seem to work :(*
```bash
WITHOUT_CHECK_API=true
```
---
#### [Screen - start screen in detached mode](https://superuser.com/a/454914)
```bash
screen -d -m <yourcommand>
```
---
#### Gerrit - search term to view all merged non-device related changes
```
status:merged -project:^LineageOS/android_device.+  -project:^LineageOS/android_kernel.+
```
---
#### RAR Archive folders with password in background:
```bash
for i in *NEF; do screen -d -m rar a -p'password' ~/Pictures/"$i.rar" -m0 -v500M -r "$i"/* ; done
```
---
#### [`find` multiple matching names using OR operation and exec a command](https://unix.stackexchange.com/a/50613)
```bash
find . -type f \( -name "*REAL*" -o -name "*FAKE*" -o -name "*mp3" \) -exec basename {} \;
```
---
#### `find` above and create replica dir structure from the result
 - ##### *Not tested against specal characters*
```bash
 find . -type f \( -name "*REAL*" -o -name "*FAKE*" -o -name "*mp3" \) -exec dirname {} \; | xargs -I {} bash -c 'mkdir -p ./FAKES/"{}"'
```
---
#### [`find` Directory structure as CSV](https://stackoverflow.com/a/58606757)
```bash
find . -maxdepth 2 -mindepth 2 -type d | sort | sed 's:./::;s:/:",":;s:^:":;s:$:":g;' > file.csv
```
---
#### [`sed` - Convert synced LRC to unsynced LRC](https://unix.stackexchange.com/a/187894/261206)
```bash
sed -r -i 's/^\[(.*)\]//' "$FILE"
```
---
#### [RegEx to match duplicate lines](https://stackoverflow.com/questions/1573361)
```bash
^(.*)(\r?\n\1)+$
```

#### Substitute find result as argument in a command and run it in background
```bash
find -iname "*flac" -exec ls -Q {} \; | sed 's/$/ \&/; s/^/md5sum /' > ~/tmp/bg_tasks.sh
```

#### [And then run 10 threads, wait for it to finish, run 10 more.](https://stackoverflow.com/questions/356100/how-to-wait-in-bash-for-several-subprocesses-to-finish-and-return-exit-code-0)
```bash
 sed '0~10 s/$/\nwait\necho WAITING.../' < bg_tasks.sh > waiting_tasks.sh
```
---
#### [Find & display only files that do not have lyrics](https://stackoverflow.com/questions/23740545/how-to-print-only-the-unique-lines-in-bash)
```bash
find \( -name "*lrc" -o -name "*flac" \) | sed -e "s/.flac$//g;" -e "s/.lrc$//g;" | sort | uniq -u
```
---

#### [AWK - Netstat - Print time and connections](https://stackoverflow.com/questions/17001849/awk-partly-string-match-if-column-word-partly-matches)
```bash
awk -F '[[:space:]][[:space:]]+' ' $1~/TIMEST/ { print } { print $5 }' /tmp/netstat_connections.txt | head
```
---

#### [Regex match all language characters, but stop at 2nd occurrance of tab](https://stackoverflow.com/questions/2013124/regex-matching-up-to-the-first-occurrence-of-a-character)
```perl
^(ID|[0-9]+)\t+([\x00-\x7F]|[^\x00-\x7F])(.*?)\t

Example:
ID			artist	title	error
91092377	Seether	I've Got You Under My Skin	Your account can't stream the track from your current country and no alternative found.

Matches till BEFORE the TITLE column 
```
---

#### NX Tar extract manually collected bundles and strip unnecesarry folders:
```bash
for i in *tar.gz; do j="${i%.tar.gz}"; mkdir $j; tar -C $j -xf $i --strip-components=4; done
```
---

#### [Print all lines after matched pattern](https://stackoverflow.com/questions/5346896/print-everything-on-line-after-match)
```bash
awk '/### begin/ {seen = 1} seen {print}' wg0.conf
```
---
#### [AWK - Print first column after all other columns](https://stackoverflow.com/a/4198169/6437140)
```bash
$ git log --oneline COMMIT~1..COMMIT | awk '{first = $1; $1 = ""; print $0, first; }'
 <COMMITmessage> <commitsha>
```
---
#### [Log to journald](https://serverfault.com/a/573951/535443)
```bash
echo 'hello' | systemd-cat -t someapp -p emerg
# Logged as
Feb 07 13:48:56 localhost.localdomain someapp[15278]: hello
```
---
#### [Remove Zsh duplicate history](https://www.quora.com/How-do-I-remove-duplicates-and-sort-entries-in-zsh-history)
```bash
cat -n .zsh_history | sort -t ';' -uk2 | sort -nk1 | cut -f2- > .zsh_short_history

mv .zsh_short_history .zsh_history

Explanation

(1) add line number column to keep track of order: cat -n .zsh_history

(2) sort by command and keep unique commands only: sort -t ';' -uk2

note: need to set ';' as the sort delimeter because of zshell datetime stamp

(3) sort now by the line number added before: sort -nk1

(4) remove line number column added in the first step: cut -f2-

(5) save under new file: > .zsh_short_history

(6) replace zshell history file: mv .zsh_short_history .zsh_history
```
