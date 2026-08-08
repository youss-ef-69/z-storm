#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Smart Network Scanner Module
Discovers network devices and identifies targets automatically
"""

import time
import socket
import subprocess
from typing import Dict, List, Optional, Tuple
from scapy.all import ARP, Ether, srp, sniff, get_if_hwaddr
from scapy.layers.inet import IP
from scapy.layers.dhcp import DHCP


class SmartScanner:
    """
    Smart network scanner with automatic device discovery and classification
    """

    def __init__(self, interface: str = "eth0", timeout: int = 5):
        self.interface = interface
        self.timeout = timeout
        self.network_info = {
            'interface': interface,
            'mac': get_if_hwaddr(interface),
            'ip': self._get_ip(),
            'subnet': self._get_subnet(),
            'gateway': None,
            'dhcp_servers': [],
            'hosts': [],
            'devices': {
                'servers': [],
                'clients': [],
                'switches': [],
                'routers': [],
                'unknown': []
            },
            'total_hosts': 0
        }

        print(f"[+] Smart Scanner initialized on {interface}")

    def _get_ip(self) -> str:
        """Get interface IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "0.0.0.0"

    def _get_subnet(self) -> str:
        """Get subnet for scanning"""
        ip = self._get_ip()
        if ip.startswith("192.168."):
            return "192.168.1.0/24"
        elif ip.startswith("10."):
            return "10.0.0.0/24"
        elif ip.startswith("172."):
            return "172.16.0.0/24"
        else:
            return "192.168.1.0/24"

    def scan_network(self) -> Dict:
        """Scan entire network"""
        print("[+] Scanning network...")

        self._discover_gateway()
        self._discover_hosts()
        self._discover_dhcp_servers()
        self._classify_devices()

        print(f"[+] Network scan complete: {self.network_info['total_hosts']} hosts found")
        return self.network_info

    def _discover_gateway(self):
        """Discover default gateway"""
        try:
            result = subprocess.run(
                ["ip", "route", "show", "default"],
                capture_output=True, text=True
            )
            for line in result.stdout.split('\n'):
                if 'default via' in line:
                    gateway = line.split('default via')[1].split()[0]
                    self.network_info['gateway'] = gateway
                    print(f"[+] Gateway found: {gateway}")
                    return
        except:
            pass

    def _discover_hosts(self):
        """Discover all hosts on network"""
        subnet = self.network_info['subnet']
        print(f"[+] Scanning subnet: {subnet}")

        try:
            arp_request = ARP(pdst=subnet)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = broadcast / arp_request

            answered, _ = srp(packet, timeout=self.timeout,
                              iface=self.interface, verbose=False)

            for sent, received in answered:
                host = {
                    'ip': received.psrc,
                    'mac': received.hwsrc,
                    'vendor': self._get_vendor(received.hwsrc),
                    'type': 'unknown'
                }
                self.network_info['hosts'].append(host)

            self.network_info['total_hosts'] = len(self.network_info['hosts'])
            print(f"[+] Found {self.network_info['total_hosts']} hosts")

        except Exception as e:
            print(f"[-] Error scanning hosts: {e}")

    def _discover_dhcp_servers(self):
        """Discover DHCP servers"""
        print("[+] Discovering DHCP servers...")

        try:
            def dhcp_filter(packet):
                return packet.haslayer(DHCP)

            packets = sniff(iface=self.interface, filter="udp and port 67",
                            timeout=5, count=10)

            for packet in packets:
                if packet.haslayer(DHCP):
                    try:
                        dhcp_server = packet[IP].src
                        if dhcp_server not in self.network_info['dhcp_servers']:
                            self.network_info['dhcp_servers'].append(dhcp_server)
                            print(f"[+] DHCP server found: {dhcp_server}")
                    except:
                        pass

            if not self.network_info['dhcp_servers']:
                print("[!] No DHCP servers detected")

        except Exception as e:
            print(f"[-] Error detecting DHCP servers: {e}")

    def _classify_devices(self):
        """Classify discovered devices"""
        print("[+] Classifying devices...")

        for host in self.network_info['hosts']:
            host_type = self._classify_host(host['ip'])
            host['type'] = host_type

            if host_type == 'dhcp_server':
                self.network_info['devices']['servers'].append(host)
            elif host_type == 'router' or host['ip'] == self.network_info['gateway']:
                self.network_info['devices']['routers'].append(host)
            elif self._is_switch(host):
                self.network_info['devices']['switches'].append(host)
            else:
                self.network_info['devices']['clients'].append(host)

        print(f"[+] Classification complete")
        print(f"    Servers: {len(self.network_info['devices']['servers'])}")
        print(f"    Routers: {len(self.network_info['devices']['routers'])}")
        print(f"    Switches: {len(self.network_info['devices']['switches'])}")
        print(f"    Clients: {len(self.network_info['devices']['clients'])}")

    def _classify_host(self, ip: str) -> str:
        """Classify a single host"""
        common_ports = {
            22: 'ssh', 23: 'telnet', 80: 'http',
            443: 'https', 53: 'dns', 67: 'dhcp_server',
            68: 'dhcp_client', 69: 'tftp', 445: 'smb'
        }

        for port, service in common_ports.items():
            if self._check_port(ip, port):
                if service == 'dhcp_server':
                    return 'dhcp_server'
                elif service in ['http', 'https', 'ssh']:
                    return 'server'

        return 'client'

    def _check_port(self, ip: str, port: int) -> bool:
        """Check if port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False

    def _is_switch(self, host: Dict) -> bool:
        """Determine if device is a switch"""
        switch_ouis = ['00:1a:11', '00:1c:42', '00:05:69', '00:1d:71']
        mac = host['mac'].lower()

        for oui in switch_ouis:
            if mac.startswith(oui.lower()):
                return True
        return False

    def _get_vendor(self, mac: str) -> str:
        """Get vendor from MAC address"""
        vendors = {
            '00:0c:29': 'VMware',
            '00:50:56': 'VMware',
            '00:05:69': 'Cisco',
            '00:1a:11': 'Cisco',
            '00:1c:42': 'Cisco',
            '08:00:27': 'VirtualBox',
            '52:54:00': 'QEMU/KVM',
            '00:16:3e': 'Xen',
            '00:15:5d': 'Microsoft',
            '00:1d:71': 'Dell',
            '00:1e:68': 'Intel'
        }

        mac_prefix = mac[:8].upper()
        return vendors.get(mac_prefix, 'Unknown')

    def get_attack_targets(self) -> Dict:
        """Identify recommended attack targets"""
        targets = {
            'dhcp_servers': [],
            'hosts_for_arp_spoofing': [],
            'recommended_attack': None
        }

        if self.network_info['dhcp_servers']:
            targets['dhcp_servers'] = self.network_info['dhcp_servers']

        if self.network_info['gateway']:
            for host in self.network_info['hosts']:
                if host['ip'] != self.network_info['gateway'] and host['ip'] != self.network_info['ip']:
                    if host['type'] == 'client':
                        targets['hosts_for_arp_spoofing'].append(host['ip'])

        if targets['dhcp_servers']:
            targets['recommended_attack'] = 'dhcp_starvation'
        elif targets['hosts_for_arp_spoofing']:
            targets['recommended_attack'] = 'arp_spoofing'
        else:
            targets['recommended_attack'] = 'full_attack'

        return targets

    def print_network_info(self):
        """Print network information"""
        print("\n" + "=" * 50)
        print("🌐 Network Information")
        print("=" * 50)
        print(f"Interface : {self.network_info['interface']}")
        print(f"Your IP   : {self.network_info['ip']}")
        print(f"Gateway   : {self.network_info['gateway']}")
        print(f"Subnet    : {self.network_info['subnet']}")
        print(f"Hosts     : {self.network_info['total_hosts']}")
        print(f"DHCP Servers: {len(self.network_info['dhcp_servers'])}")
        print("-" * 50)

        for category, devices in self.network_info['devices'].items():
            if devices:
                print(f"\n📂 {category.upper()}:")
                for dev in devices[:5]:
                    print(f"  • {dev['ip']} ({dev['mac']}) - {dev.get('vendor', 'Unknown')}")
                if len(devices) > 5:
                    print(f"  ... and {len(devices) - 5} more")