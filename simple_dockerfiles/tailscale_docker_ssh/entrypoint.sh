#!/bin/bash
tailscaled --tun=userspace-networking --socks5-server=localhost:1055 --outbound-http-proxy-listen=localhost:1055 &
tailscale up --accept-dns=false --accept-routes=false --hostname ctop --ssh --auth-key "${TS_AUTH_KEY}"
sleep infinity
