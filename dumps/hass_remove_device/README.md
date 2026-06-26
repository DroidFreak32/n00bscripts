# Home Assistant: Stale Device Force-Removal Guide

This guide explains how to permanently force-remove stale devices and their associated entities from your Home Assistant instance when the integration that created them doesn't support individual device removal.

---

## 📌 Context (The Bottleneck)
Normally, when you click **Delete** on a device, Home Assistant asks the integration if it supports dynamic device removal. For many integrations (like the Hikvision NVR or other multi-device setups), this is not supported, resulting in a `Config entry does not support device removal` error.

To bypass this, we must stop Home Assistant and surgically remove the device and its entities from the internal registry files.

---

## 🛠️ Prerequisites
* **Host**: `<your-ssh-host>` (Raspberry Pi running Docker)
* **Config Directory**: `/home/<your-username>/containers/data/homeassistant/config`
* **Python**: Python 3 installed on the host (for safe JSON parsing/editing).

---

## 🚀 Step-by-Step Guide

### Step 1: Identify the Stale Device ID
Locate the **32-character hex ID** of the device you want to remove.
* You can easily grab it from the URL of the device page in the Home Assistant UI:
  `http://<your-ha-ip>:8123/config/devices/device/081c045b28b59d25ed52f94a5cbd2558`
  *(Here, the Device ID is `081c045b28b59d25ed52f94a5cbd2558`)*

---

### Step 2: SSH into your Host
Use your SSH connection to log into your Home Assistant host:
```bash
SSH_AUTH_SOCK=$(gpgconf --list-dirs agent-ssh-socket) ssh <your-ssh-host>
```

---

### Step 3: Copy the Cleanup Script to the Host
You can copy the pre-built [clean_device.py](clean_device.py) script to your host machine.
Alternatively, create it on the host using `nano /tmp/clean_device.py` and paste the contents of [clean_device.py](clean_device.py) there.

---

### Step 4: Perform the Cleanup
Execute the following commands on the host machine.

1. **Back up your registries (Crucial)**:
   ```bash
   sudo cp /home/<your-username>/containers/data/homeassistant/config/.storage/core.device_registry /home/<your-username>/containers/data/homeassistant/config/.storage/core.device_registry.bak
   sudo cp /home/<your-username>/containers/data/homeassistant/config/.storage/core.entity_registry /home/<your-username>/containers/data/homeassistant/config/.storage/core.entity_registry.bak
   ```

2. **Stop the Home Assistant Container**:
   *(Home Assistant must be stopped so it doesn't overwrite your manual registry changes on shutdown).*
   ```bash
   sudo docker stop homeassistant
   ```

3. **Run the Script**:
   Run the python script, passing the target **Device ID** as the argument:
   ```bash
   sudo python3 /tmp/clean_device.py <DEVICE_ID>
   ```
   *Example:*
   ```bash
   sudo python3 /tmp/clean_device.py 081c045b28b59d25ed52f94a5cbd2558
   ```

4. **Restart Home Assistant**:
   If the script completes successfully, start the container again:
   ```bash
   sudo docker start homeassistant
   ```

---

## 🔄 Rollback / Recovery Plan
If anything goes wrong or Home Assistant fails to start due to corrupted registry files, you can easily restore your backups:

1. Stop the container (if running):
   ```bash
   sudo docker stop homeassistant
   ```
2. Restore the backup files:
   ```bash
   sudo cp /home/<your-username>/containers/data/homeassistant/config/.storage/core.device_registry.bak /home/<your-username>/containers/data/homeassistant/config/.storage/core.device_registry
   sudo cp /home/<your-username>/containers/data/homeassistant/config/.storage/core.entity_registry.bak /home/<your-username>/containers/data/homeassistant/config/.storage/core.entity_registry
   ```
3. Restart Home Assistant:
   ```bash
   sudo docker start homeassistant
   ```

---

## 📝 The Cleanup Script (`clean_device.py`)
This script safely parses the registry JSON files, filters out the target device and any entities associated with it, and writes the clean data back. It uses only Python's standard library.

*(Refer to [clean_device.py](clean_device.py) in this workspace to copy the full code).*
