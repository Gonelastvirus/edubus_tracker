#!/bin/bash

# Exit immediately if a command fails
set -e

# Install Rust in temporary location
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y -q
sleep 2

# Set Cargo/Rust paths to /tmp (writable on Render free plan)
export CARGO_HOME=/tmp/.cargo
export RUSTUP_HOME=/tmp/.rustup
export PATH=$CARGO_HOME/bin:$PATH
sleep 2

# Upgrade pip and install dependencies
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
