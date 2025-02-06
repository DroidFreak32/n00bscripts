### 1440p-ready Sunshine Streaming VM on GCP

#### Instance Configuration:

OS: `Latest Ubuntu LTS release`		
GPU: `NVIDIA L4`	
Machine Type: `g2-standard-8`	
VPC: Prefer a Dual-Stack subnet for direct IPv6 connectivity with `tailscale`.


#### Steps

#### Preparing the VM

Note: Preferably run these in a `tmux`/`screen` session

- Download the latest NVIDIA GRID driver:

```bash
GRID_VERSION_LATEST=$(gcloud storage ls gs://nvidia-drivers-us-public/GRID --format=gsutil | tail -n1)
GRID_DRIVER_LATEST=$(gcloud storage ls  $GRID_VERSION_LATEST | grep -E "^gs.*grid.run$")
gcloud storage cp "$GRID_DRIVER_LATEST" .
```

- Download the latest sunshine deb
```bash
wget https://github.com/LizardByte/Sunshine/releases/download/v0.23.1/sunshine-ubuntu-24.04-amd64.deb
```

- Download the necessary dependencies & other useful packages
```bash
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install dkms menu build-essential libvulkan1 libglvnd* pkg-config mangohud mangohudctl gamemode xfce4 cockpit bat xdg-utils udisks2-btrfs udisks2-lvm2 xfce4-power-manager libc6:1386 -y
```

- Download and install the latest Steam Installer:
```bash
wget https://cdn.fastly.steamstatic.com/client/installer/steam.deb
sudo apt install -f ./steam.deb
```

- Upgrade & Reboot the system to ensure matching kernel versions
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```


#### Installing NVIDIA drivers and a Dummy Monitor for Streaming

- Install the NVIDIA GRID driver
```bash
sudo bash ~/NVIDIA-Linux-x86_64-550.127.05-grid.run -a
```

- Run `nvidia-xconfig` to generate a template `/etc/X11/xorg.conf`
```bash
sudo nvidia-xconfig
```

- Modify the `Screen` section of `/etc/X11/xorg.conf` to add the dummy Monitor options:

```ini
    Option         "MetaModes" "DP-0: 2560x1440_60 +0+0"
    Option         "ConnectedMonitor" "DP-0"

```

It should look like this, feel free to modify the resolution:
```ini
... Other Entries above ...

Section "Screen"
    Identifier     "Screen0"
    Device         "Device0"
    Monitor        "Monitor0"
    DefaultDepth    24
    Option         "MetaModes" "DP-0: 2560x1440_60 +0+0"
    Option         "ConnectedMonitor" "DP-0"
    SubSection     "Display"
        Depth       24
    EndSubSection
EndSection
```

#### Autologin into the Desktop Environment

- Reboot the VM again & SSH back into it
- Now, `loginctl` should show a session with user `lightdm`
```bash
$ loginctl
SESSION  UID USER       SEAT  TTY STATE  IDLE SINCE
      2 1001 <redacted> -     -   active no   -
     c1  112 lightdm    seat0 -   active no   -
```

- Next, we need to configure lightdm to start `xfce4` and [autologin to our user without prompting for a password](https://wiki.archlinux.org/title/LightDM#Enabling_autologin)
- Create and join required groups
```bash
sudo groupadd -r autologin
sudo gpasswd -a $USER autologin
sudo groupadd -r nopasswdlogin
sudo gpasswd -a $USER nopasswdlogin
```
- Set the `/etc/lightdm/lightdm.conf
```bash
cat << EOF | sudo tee /etc/lightdm/lightdm.conf
[Seat:*]
autologin-user=$USER
autologin-session=xfce
EOF
```

- Ensure `/etc/pam.d/lightdm` has this line
```bash
auth        sufficient  pam_succeed_if.so user ingroup nopasswdlogin
```

- Reboot and now `loginctl` should show your _username_ having 2 sessions

#### Install & enable Sunshine as a service on boot
```bash
sudo apt install -f ~/sunshine-ubuntu-24.04-amd64.deb

mkdir -p ~/.config/systemd/user/

cat << EOF > ~/.config/systemd/user/sunshine.service
[Unit]
Description=Sunshine self-hosted game stream host for Moonlight.
StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
ExecStartPre=/bin/sleep 30
ExecStart=/usr/bin/sunshine
Restart=on-failure
RestartSec=5s
#Flatpak Only
#ExecStop=flatpak kill dev.lizardbyte.sunshine

[Install]
WantedBy=default.target
EOF


systemctl --user enable sunshine.service
```

- Install tailscale to add the pin
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

- Start sunshine:
```bash
systemctl restart --user sunshine.service
```

- Enter `https://<tailscale IP>:47990` in your browser to configure sunshine
- Add this IP in Moonlight to generate the Pin, enter this pin in sunshine's webui

DONE!

Incase you see a blank screen, it could be xfce4 power saving, in which case restart your system, connect via moonlight and adjust the power manager settings.
