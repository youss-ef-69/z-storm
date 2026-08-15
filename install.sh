#!/bin/bash
# ============================================================
# Z-Storm Installation Script v2.0.0
# Developed by: Youssef Zedan
# ============================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[*]${NC} $1"; }
print_success() { echo -e "${GREEN}[+]${NC} $1"; }
print_error() { echo -e "${RED}[!]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[⚠]${NC} $1"; }

# Print banner
echo -e "${CYAN}"
echo "███████╗    ███████╗████████╗ ██████╗ ██████╗ ███╗   ███╗"
echo "╚══███╔╝    ██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗████╗ ████║"
echo -e "${PURPLE}  ███╔╝     ███████╗   ██║   ██║   ██║██████╔╝██╔████╔██║"
echo " ███╔╝      ╚════██║   ██║   ██║   ██║██╔══██╗██║╚██╔╝██║"
echo -e "${CYAN}███████╗    ███████║   ██║   ╚██████╔╝██║  ██║██║ ╚═╝ ██║"
echo "╚══════╝    ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝"
echo -e "${NC}"
echo -e "${GREEN}         Z-Storm Installation Script v2.0.0${NC}"
echo -e "${YELLOW}         Developed by: Youssef Zedan${NC}"
echo -e "${BLUE}         ⚡ APT-Based Installation${NC}"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (sudo ./install.sh)"
    exit 1
fi

print_success "Running as root user"

# ============================================================
# 1. Detect OS
# ============================================================
print_info "Detecting operating system..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    print_error "Cannot detect OS"
    exit 1
fi
print_success "Detected OS: $OS $VERSION"

# ============================================================
# 2. Install Scapy and dependencies via APT
# ============================================================
print_info "Updating package lists..."
apt-get update -y --quiet=2

print_info "Installing Scapy and dependencies via APT..."
apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-scapy \
    python3-netifaces \
    python3-yaml

# ============================================================
# 3. Install additional Python packages (lightweight)
# ============================================================
print_info "Installing additional Python packages..."
pip3 install --no-cache-dir --no-deps \
    tqdm \
    colorama \
    jinja2 \
    tabulate 2>/dev/null || print_warning "Some packages failed (optional)"

# ============================================================
# 4. Verify Scapy installation
# ============================================================
print_info "Verifying Scapy installation..."
if python3 -c "import scapy" 2>/dev/null; then
    print_success "Scapy installed successfully!"
else
    print_error "Scapy installation failed. Trying pipx fallback..."
    apt-get install -y pipx
    pipx install scapy
    pipx ensurepath
fi

# ============================================================
# 5. Create directories
# ============================================================
print_info "Creating directories..."
mkdir -p reports logs
chmod 755 reports logs

# ============================================================
# 6. Set permissions and symlink
# ============================================================
chmod +x zstorm.py
ln -sf $(pwd)/zstorm.py /usr/local/bin/zstorm 2>/dev/null

# ============================================================
# 7. Create config.yaml if missing
# ============================================================
if [ ! -f "config.yaml" ]; then
    print_info "Creating default config.yaml..."
    cat > config.yaml << 'EOF'
interface: eth0
attack:
  mode: "intelligent"
  type: "dhcp_starvation"
  threads: 5
  max_macs: 10000
dtp_spoofing:
  enabled: false
  interval: 5.0
  domain: "z-storm-vlan"
arp_spoofing:
  enabled: false
  interval: 2.0
logging:
  level: "INFO"
  file: "zstorm.log"
EOF
fi

# ============================================================
# 8. Final summary
# ============================================================
echo ""
echo "=========================================="
echo "        Installation Complete!"
echo "=========================================="
echo ""
print_success "Z-Storm v2.0.0 installed successfully!"
echo ""
print_info "Installed via APT:"
echo "  python3, python3-pip"
echo "  python3-scapy, python3-netifaces, python3-yaml"
echo ""
print_success "Run Z-Storm:"
echo "  sudo zstorm -h"
echo "  sudo zstorm -i eth0 --type dtp_spoofing --dtp"
echo ""
print_warning "REMEMBER: This tool is for EDUCATIONAL use only!"
echo "=========================================="
