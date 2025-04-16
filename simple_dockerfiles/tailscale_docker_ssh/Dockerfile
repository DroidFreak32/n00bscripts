FROM debian:bookworm-slim

RUN apt update && apt install -y curl dialog rclone

RUN curl -fsSL https://tailscale.com/install.sh | sh

COPY entrypoint.sh /entrypoint.sh

#ENTRYPOINT /entrypoint.sh "$@"

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
