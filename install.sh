#!/bin/bash
# Z-Storm Installation Script

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              Z-Storm Installer                       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"

# Check Python
if ! command -v python3 &>/dev/null; then
    echo -e "${YELLOW}[!] Python 3 not found. Installing...${NC}"
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
fi

# Install dependencies
echo -e "${GREEN}[+] Installing dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y tcpdump arp-scan nmap

sudo apt install -y python3-scapy python3-requests python3-yaml python3-colorama

# Create system-wide command
echo -e "${GREEN}[+] Setting up system-wide 'zstorm' command ...${NC}"

sudo tee /usr/local/bin/zstorm > /dev/null << 'EOF'
#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
python3 "$SCRIPT_DIR/zstorm.py" "$@"
EOF

sudo chmod +x /usr/local/bin/zstorm

echo -e "${GREEN}[+] Done! You can now run 'zstorm' from anywhere in the terminal.${NC}"

# 
echo -e "${GREEN}[+] Installation complete!${NC}"
echo -e "${GREEN}[+] You can now run 'zstorm' from ANYWHERE in the terminal.${NC}"
echo -e "${YELLOW}[!] Don't forget to edit 'config.yaml' before running.${NC}"
