#!/bin/bash
# ============================================================
# Z-Storm Installation Script v2.1 (Lightning Fast)
# Developed by: Youssef Zedan
# ============================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored messages
print_info() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_error() {
    echo -e "${RED}[!]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

# Print banner
echo ""
echo "███████╗    ███████╗████████╗ ██████╗ ██████╗ ███╗   ███╗"
echo "╚══███╔╝    ██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗████╗ ████║"
echo "  ███╔╝     ███████╗   ██║   ██║   ██║██████╔╝██╔████╔██║"
echo " ███╔╝      ╚════██║   ██║   ██║   ██║██╔══██╗██║╚██╔╝██║"
echo "███████╗    ███████║   ██║   ╚██████╔╝██║  ██║██║ ╚═╝ ██║"
echo "╚══════╝    ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝"
echo ""
echo "         Z-Storm Installation Script v2.1"
echo "         Developed by: Youssef Zedan"
echo "         ⚡ Lightning Fast Mode"
echo ""

# ============================================================
# 1. Check if running as root
# ============================================================
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (sudo ./install.sh)"
    exit 1
fi

print_success "Running as root user"

# ============================================================
# 2. Detect OS and Package Manager
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
# 3. Update Package Lists (Lightweight - NO UPGRADE)
# ============================================================
print_info "Updating package lists (lightweight)..."
print_warning "Skipping system upgrade to save time"

if command -v apt-get &> /dev/null; then
    apt-get update -y --quiet=2
elif command -v yum &> /dev/null; then
    yum check-update -y
elif command -v dnf &> /dev/null; then
    dnf check-update -y
else
    print_warning "Could not update package lists (no known package manager)"
fi

print_success "Package lists updated"

# ============================================================
# 4. Install Python3 and pip (Minimal)
# ============================================================
print_info "Installing Python3 and pip (minimal)..."

if command -v apt-get &> /dev/null; then
    apt-get install -y --no-install-recommends python3 python3-pip python3-venv
elif command -v yum &> /dev/null; then
    yum install -y python3 python3-pip
elif command -v dnf &> /dev/null; then
    dnf install -y python3 python3-pip
else
    print_warning "Could not install Python (no known package manager)"
fi

# ============================================================
# 5. Install System Dependencies (Minimal)
# ============================================================
print_info "Installing system dependencies (minimal)..."

if command -v apt-get &> /dev/null; then
    apt-get install -y --no-install-recommends \
        tcpdump \
        net-tools \
        iproute2 \
        ethtool \
        build-essential \
        python3-dev \
        libpcap-dev
elif command -v yum &> /dev/null; then
    yum install -y \
        tcpdump \
        net-tools \
        iproute \
        ethtool \
        gcc \
        python3-devel \
        libpcap-devel
elif command -v dnf &> /dev/null; then
    dnf install -y \
        tcpdump \
        net-tools \
        iproute \
        ethtool \
        gcc \
        python3-devel \
        libpcap-devel
fi

print_success "System dependencies installed"

# ============================================================
# 6. Install Python Dependencies (Fast)
# ============================================================
print_info "Installing Python packages (fast mode)..."

# Skip pip upgrade to save time
# python3 -m pip install --upgrade pip

# Install only essential packages (no extra packages)
print_info "Installing core packages (essential only)..."
pip3 install --no-cache-dir --no-deps \
    scapy \
    netifaces \
    pyyaml \
    tqdm \
    colorama \
    jinja2 \
    tabulate

# Install dependencies for the packages (minimal)
pip3 install --no-cache-dir \
    requests \
    psutil

print_success "Python packages installed"

# Check if scapy was installed correctly
print_info "Verifying Scapy installation..."
python3 -c "from scapy.all import *; print('Scapy installed successfully')" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "Scapy installed successfully"
else
    print_warning "Scapy may not be installed correctly. Installing with extra options..."
    pip3 install --no-cache-dir scapy --ignore-installed
fi

# ============================================================
# 7. Create Directories
# ============================================================
print_info "Creating directories..."

# Create main directories
mkdir -p reports
mkdir -p logs

# Set permissions
chmod 755 reports
chmod 755 logs

print_success "Directories created: reports/, logs/"

# ============================================================
# 8. Check Module Files (Skip if not needed)
# ============================================================
print_info "Checking module files..."

MODULES_DIR="modules"
MODULES=(
    "__init__.py"
    "smart_scanner.py"
    "advanced_report.py"
    "arp_spoof.py"
    "auto_lab.py"
    "dtp_spoof.py"
)

MISSING_MODULES=()
for module in "${MODULES[@]}"; do
    if [ ! -f "$MODULES_DIR/$module" ]; then
        MISSING_MODULES+=("$module")
    fi
done

if [ ${#MISSING_MODULES[@]} -eq 0 ]; then
    print_success "All module files present"
else
    print_warning "Missing modules: ${MISSING_MODULES[*]}"
    print_info "Please ensure all module files are present before running"
fi

# ============================================================
# 9. Set Permissions
# ============================================================
print_info "Setting permissions..."

# Make main script executable
chmod +x zstorm.py 2>/dev/null
chmod +x install.sh 2>/dev/null

print_success "Permissions set"

# ============================================================
# 10. Create config.yaml if missing
# ============================================================
print_info "Checking config file..."

if [ ! -f "config.yaml" ]; then
    print_warning "config.yaml not found. Creating default..."
    cat > config.yaml << 'EOF'
# Z-Storm Configuration

interface: eth0

attack:
  mode: "intelligent"
  type: "dhcp_starvation"
  threads: 5
  max_macs: 10000
  delay_min: 0.001
  delay_max: 0.01
  timeout: 300

dtp_spoofing:
  enabled: false
  interval: 5.0
  domain: "z-storm-vlan"
  status: 3
  vtp: 1
  neighbor: 1

smart_scanner:
  enabled: true
  timeout: 5
  classify_devices: true

arp_spoofing:
  enabled: false
  interval: 2.0
  restore_on_exit: true

reporting:
  enabled: true
  formats: ["json", "html", "markdown"]
  save_path: "reports/"

logging:
  level: "INFO"
  file: "zstorm.log"
  max_size_mb: 10
  backup_count: 3
EOF
    print_success "Default config.yaml created"
else
    print_success "config.yaml exists"
fi

# ============================================================
# 11. Check Python Version
# ============================================================
print_info "Checking Python version..."

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.6"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    print_success "Python version $PYTHON_VERSION (OK)"
else
    print_warning "Python version $PYTHON_VERSION (min required: $REQUIRED_VERSION)"
    print_info "Consider upgrading Python"
fi

# ============================================================
# 12. Test Run (Skip to save time)
# ============================================================
print_info "Quick test..."

python3 -c "import sys; sys.path.insert(0, '.'); from modules import *; print('Modules imported successfully')" 2>/dev/null

if [ $? -eq 0 ]; then
    print_success "Z-Storm modules loaded correctly"
else
    print_warning "Module import test failed. Please check your setup."
fi

# ============================================================
# 13. Final Summary
# ============================================================
echo ""
echo "=========================================="
echo "        Installation Complete!"
echo "=========================================="
echo ""
print_success "Z-Storm v2.1.0 installed successfully!"
echo ""
print_info "What's installed (Fast Mode):"
echo "  📦 Python 3.x"
echo "  📦 Scapy (packet manipulation)"
echo "  📦 netifaces (interface detection)"
echo "  📦 pyyaml (configuration)"
echo "  📦 tqdm (progress bars)"
echo "  📦 colorama (colored output)"
echo "  📦 jinja2 (HTML reports)"
echo "  📦 tabulate (table formatting)"
echo ""
print_info "Directory structure:"
echo "  📁 reports/ - Generated reports"
echo "  📁 logs/    - Log files"
echo "  📁 modules/ - All modules"
echo ""
print_info "Configuration:"
echo "  📄 config.yaml - Edit to customize"
echo ""
print_success "Run Z-Storm:"
echo "  sudo python3 zstorm.py -h"
echo "  sudo python3 zstorm.py -i eth0 --type dhcp_starvation"
echo "  sudo python3 zstorm.py -i eth0 --type dtp_spoofing"
echo ""
print_warning "⚠️  REMEMBER: This tool is for EDUCATIONAL use only!"
print_warning "⚠️  Unauthorized use is ILLEGAL!"
echo ""
echo "=========================================="
