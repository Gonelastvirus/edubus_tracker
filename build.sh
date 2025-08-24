#!/bin/bash
set -e

# Skip Rust installation; just set local Cargo paths
export CARGO_HOME=/tmp/.cargo
export RUSTUP_HOME=/tmp/.rustup
export PATH=$CARGO_HOME/bin:$PATH

# Upgrade pip and install dependencies
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
