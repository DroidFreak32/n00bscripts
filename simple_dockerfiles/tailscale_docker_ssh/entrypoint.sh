#!/bin/bash

# Define cleanup procedure: https://stackoverflow.com/a/41451517/6437140
cleanup() {
    echo "Container stopped, performing cleanup..."
    tailscale logout
}

# Trap SIGTERM
trap 'cleanup' SIGTERM

# Execute a command
tailscaled --tun=userspace-networking --socks5-server=localhost:1055 --outbound-http-proxy-listen=localhost:1055 &
tailscale up --accept-dns=false --accept-routes=false --hostname ctop --ssh --auth-key "${TS_AUTH_KEY}"

echo "TS Initialized"

sleep infinity &

# Wait
wait $!
