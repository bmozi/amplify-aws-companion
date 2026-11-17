# Local, network-disabled execution image for a packaged companion archive.
# Image construction fetches tools; the later check run has no network or AWS credentials.
FROM python:3.13-slim@sha256:ffb752e139c0a19692a43af8d8523b274222dd68eebad5d583b45c2201c6e30a
ARG TARGETARCH

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl xz-utils unzip git openssl \
    && rm -rf /var/lib/apt/lists/*

RUN set -eu; cd /tmp; \
    case "$TARGETARCH" in \
      arm64) node_arch=arm64; terraform_arch=arm64 ;; \
      amd64) node_arch=x64; terraform_arch=amd64 ;; \
      *) echo "Unsupported target architecture: $TARGETARCH" >&2; exit 2 ;; \
    esac; \
    node_file="node-v22.23.2-linux-${node_arch}.tar.xz"; \
    terraform_file="terraform_1.6.4_linux_${terraform_arch}.zip"; \
    curl -fsSLO "https://nodejs.org/dist/v22.23.2/${node_file}"; \
    curl -fsSLO https://nodejs.org/dist/v22.23.2/SHASUMS256.txt; \
    grep "  ${node_file}$" SHASUMS256.txt | sha256sum -c -; \
    tar -xJf "$node_file" -C /opt; \
    ln -s "/opt/node-v22.23.2-linux-${node_arch}/bin/node" /usr/local/bin/node; \
    ln -s "/opt/node-v22.23.2-linux-${node_arch}/bin/npm" /usr/local/bin/npm; \
    curl -fsSLO "https://releases.hashicorp.com/terraform/1.6.4/${terraform_file}"; \
    curl -fsSLO https://releases.hashicorp.com/terraform/1.6.4/terraform_1.6.4_SHA256SUMS; \
    grep "  ${terraform_file}$" terraform_1.6.4_SHA256SUMS | sha256sum -c -; \
    unzip -q "$terraform_file" -d /usr/local/bin; \
    rm -f "$node_file" SHASUMS256.txt "$terraform_file" terraform_1.6.4_SHA256SUMS

WORKDIR /work
