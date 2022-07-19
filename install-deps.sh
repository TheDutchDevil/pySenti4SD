#!/bin/sh

DEBIAN_FRONTEND=noninteractive

apt-get update

apt-get install -y \
    --no-install-recommends \
    openjdk-8-jdk-headless \
    python3.8 \
    python3-pip \
    python-is-python3 \
    build-essential \
    python3.8-dev 

pip3 install -r requirements.txt
