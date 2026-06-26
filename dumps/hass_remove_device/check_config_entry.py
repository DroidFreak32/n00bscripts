import os
import sys
import json
import websocket

# Home Assistant details
HASS_URL = "ws://<your-ha-ip>:8123/api/websocket"
TARGET_CONFIG_ENTRY = "<target-config-entry-id>"

# Get token from environment
TOKEN = os.environ.get("HASS_TOKEN")
if not TOKEN:
    print("Error: HASS_TOKEN environment variable not set.", file=sys.stderr)
    sys.exit(1)

def on_message(ws, message):
    data = json.loads(message)
    
    if data.get("type") == "auth_required":
        auth_msg = {
            "type": "auth",
            "access_token": TOKEN
        }
        ws.send(json.dumps(auth_msg))
        
    elif data.get("type") == "auth_ok":
        list_msg = {
            "id": 1,
            "type": "config/device_registry/list"
        }
        ws.send(json.dumps(list_msg))
        
    elif data.get("type") == "result":
        if data.get("id") == 1:
            devices = data.get("result", [])
            associated_devices = []
            for d in devices:
                if TARGET_CONFIG_ENTRY in d.get("config_entries", []):
                    associated_devices.append({
                        "id": d.get("id"),
                        "name": d.get("name"),
                        "name_by_user": d.get("name_by_user"),
                        "model": d.get("model")
                    })
            
            print(f"Found {len(associated_devices)} devices associated with config entry {TARGET_CONFIG_ENTRY}:")
            print(json.dumps(associated_devices, indent=2))
            ws.close()

def on_error(ws, error):
    print(f"Error: {error}", file=sys.stderr)

def on_close(ws, close_status_code, close_msg):
    pass

def on_open(ws):
    pass

if __name__ == "__main__":
    ws = websocket.WebSocketApp(HASS_URL,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever()
