#!/usr/bin/env python3
import json
import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Force-remove a stale device and its entities from Home Assistant registries.")
    parser.add_argument("device_id", help="The 32-character hex ID of the device to remove.")
    parser.add_argument("--config-dir", help="Path to the Home Assistant config directory (contains .storage/).", 
                        default='/home/<your-username>/containers/data/homeassistant/config')
    args = parser.parse_args()

    device_id = args.device_id
    config_dir = args.config_dir

    dev_reg_path = os.path.join(config_dir, '.storage/core.device_registry')
    ent_reg_path = os.path.join(config_dir, '.storage/core.entity_registry')

    # Verify paths
    if not os.path.exists(dev_reg_path) or not os.path.exists(ent_reg_path):
        print(f"Error: Could not find registry files in {config_dir}/.storage/", file=sys.stderr)
        print("Please check the --config-dir path.", file=sys.stderr)
        sys.exit(1)

    # 1. Clean Device Registry
    print(f"Reading device registry: {dev_reg_path}")
    try:
        with open(dev_reg_path, 'r') as f:
            dev_data = json.load(f)
    except Exception as e:
        print(f"Error reading device registry: {e}", file=sys.stderr)
        sys.exit(1)

    devices = dev_data['data']['devices']
    original_dev_count = len(devices)
    new_devices = [d for d in devices if d.get('id') != device_id]
    
    dev_removed = original_dev_count - len(new_devices)

    # 2. Clean Entity Registry
    print(f"Reading entity registry: {ent_reg_path}")
    try:
        with open(ent_reg_path, 'r') as f:
            ent_data = json.load(f)
    except Exception as e:
        print(f"Error reading entity registry: {e}", file=sys.stderr)
        sys.exit(1)

    entities = ent_data['data']['entities']
    original_ent_count = len(entities)
    new_entities = [e for e in entities if e.get('device_id') != device_id]
    ent_removed = original_ent_count - len(new_entities)

    if dev_removed == 0 and ent_removed == 0:
        print(f"No active device or entities found with ID: {device_id}")
        sys.exit(0)

    # Perform writes
    if dev_removed > 0:
        dev_data['data']['devices'] = new_devices
        try:
            with open(dev_reg_path, 'w') as f:
                json.dump(dev_data, f, indent=4)
            print(f"Removed device from registry. Count: {original_dev_count} -> {len(new_devices)}")
        except Exception as e:
            print(f"Error writing device registry: {e}", file=sys.stderr)
            sys.exit(1)

    if ent_removed > 0:
        ent_data['data']['entities'] = new_entities
        try:
            with open(ent_reg_path, 'w') as f:
                json.dump(ent_data, f, indent=4)
            print(f"Removed {ent_removed} entities from registry. Count: {original_ent_count} -> {len(new_entities)}")
        except Exception as e:
            print(f"Error writing entity registry: {e}", file=sys.stderr)
            sys.exit(1)

    print("Cleanup completed successfully.")

if __name__ == '__main__':
    main()
