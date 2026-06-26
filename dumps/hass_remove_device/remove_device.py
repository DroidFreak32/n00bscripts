import os
import sys
import json
import websocket

# Home Assistant details
HASS_URL = "ws://100.65.55.22:8123/api/websocket"
DEVICE_ID = "081c045b28b59d25ed52f94a5cbd2558"

# Get token from environment
TOKEN = os.environ.get("HASS_TOKEN")
if not TOKEN:
    print("Error: HASS_TOKEN environment variable not set.", file=sys.stderr)
    sys.exit(1)

def on_message(ws, message):
    data = json.loads(message)
    print(f"Received: {json.dumps(data, indent=2)}")
    
    if data.get("type") == "auth_required":
        print("Sending auth...")
        auth_msg = {
            "type": "auth",
            "access_token": TOKEN
        }
        ws.send(json.dumps(auth_msg))
        
    elif data.get("type") == "auth_ok":
        print("Auth successful! Sending update device (disable) command...")
        update_msg = {
            "id": 3,
            "type": "config/device_registry/update",
            "device_id": DEVICE_ID,
            "disabled_by": "user"
        }
        ws.send(json.dumps(update_msg))
        
    elif data.get("type") == "result":
        if data.get("id") == 3:
            if data.get("success"):
                print("Successfully disabled the device!")
                print("Result:", json.dumps(data.get("result"), indent=2))
            else:
                print(f"Failed to disable device: {data.get('error', {}).get('message', 'Unknown error')}")
            ws.close()
            
    elif data.get("type") == "auth_invalid":
        print(f"Authentication failed: {data.get('message')}", file=sys.stderr)
        ws.close()
        sys.exit(1)

def on_error(ws, error):
    print(f"Error: {error}", file=sys.stderr)

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def on_open(ws):
    print("Connection opened")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(HASS_URL,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever()
