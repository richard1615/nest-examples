#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo) to install NeST and its dependencies."
    exit
fi

# Function to check if a command is available
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install NeST python package
install_nest() {
    echo "Installing NeST python package..."
    
    # Ensure Python 3 is installed
    if ! command_exists python3; then
        echo "Python 3 is required. Please install Python 3 before running this script."
        exit 1
    fi

    # Ensure pip is installed
    if ! command_exists pip3; then
        echo "Installing pip..."
        apt-get update
        apt-get install -y python3-pip
    fi

    # Upgrade pip
    pip3 install -U pip

    # Install NeST from PyPi
    pip3 install nest
}

# Function to install NeST dependencies
install_dependencies() {
    echo "Installing NeST dependencies..."

    # Install core dependencies
    apt-get install -y iproute2
    apt-get install -y iputils-ping
    apt-get install -y netperf

    # Install optional dependencies
    apt-get install -y iperf3

    # Install matplotlib
    pip3 install matplotlib==3.5
}

# Main script

echo "Installing NeST and its dependencies..."

install_nest
install_dependencies

echo "NeST and its dependencies installed successfully."
