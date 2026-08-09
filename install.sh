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

# تثبيت مكتبات بايثون المطلوبة (تمت إضافة netifaces)
sudo apt install -y python3-scapy python3-requests python3-yaml python3-colorama python3-netifaces

# Create system-wide command
echo -e "${GREEN}[+] Setting up system-wide 'zstorm' command ...${NC}"

# استخدام المسار الديناميكي للمجلد الحالي (لن يحدث الخطأ مرة أخرى)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# كتابة الأمر مع sudo داخله، ليعمل مع أي مستخدم دون الحاجة لإعادة كتابة sudo
sudo tee /usr/local/bin/zstorm > /dev/null << EOF
#!/bin/bash
sudo python3 $DIR/zstorm.py "\$@"
EOF

sudo chmod +x /usr/local/bin/zstorm

echo -e "${GREEN}[+] Done! You can now run 'zstorm' from anywhere in the terminal.${NC}"
echo -e "${GREEN}[+] Installation complete!${NC}"
echo -e "${GREEN}[+] Usage: zstorm -i eth0 [--scan / -m arp]${NC}"
