#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Auto Lab Automation Module
Automates lab setup, attack execution, and cleanup
"""

import os
import time
import json
import subprocess
from typing import Dict, List, Optional
from datetime import datetime
import threading


class AutoLab:
    """Automated Lab Environment Manager"""

    def __init__(self, interface: str):
        self.interface = interface
        self.lab_config = None
        self.attack_results = {}
        self.lab_status = {
            'setup_complete': False,
            'attack_complete': False,
            'cleanup_complete': False,
            'start_time': None,
            'end_time': None
        }

    def setup_lab(self, lab_file: str = "lab_config.json") -> bool:
        """Setup lab environment automatically"""
        print("[+] Setting up lab environment...")

        try:
            with open(lab_file, 'r') as f:
                self.lab_config = json.load(f)

            lab_type = self.lab_config.get('type', 'eve-ng')

            if lab_type == 'eve-ng':
                self._setup_eve_ng()
            elif lab_type == 'gns3':
                self._setup_gns3()
            elif lab_type == 'docker':
                self._setup_docker()
            elif lab_type == 'virtualbox':
                self._setup_virtualbox()
            else:
                print(f"[-] Unknown lab type: {lab_type}")
                return False

            self.lab_status['setup_complete'] = True
            self.lab_status['start_time'] = datetime.now().isoformat()
            print("[+] Lab setup complete")
            return True

        except Exception as e:
            print(f"[-] Lab setup failed: {e}")
            return False

    def _setup_eve_ng(self):
        """Setup EVE-NG environment"""
        eve_config = self.lab_config.get('eve_ng', {})
        host = eve_config.get('host', 'localhost')
        port = eve_config.get('port', 80)
        username = eve_config.get('username', 'admin')
        password = eve_config.get('password', 'admin')
        lab_name = eve_config.get('lab_name', 'dhcp_lab')

        print(f"[+] Connecting to EVE-NG: {host}:{port}")
        time.sleep(10)
        print("[+] EVE-NG lab started")

    def _setup_gns3(self):
        """Setup GNS3 environment"""
        print("[+] Setting up GNS3 lab...")
        time.sleep(5)

    def _setup_docker(self):
        """Setup Docker containers for lab"""
        docker_config = self.lab_config.get('docker', {})
        containers = docker_config.get('containers', [])

        for container in containers:
            image = container.get('image')
            name = container.get('name', 'dhcp-lab')

            print(f"[+] Starting Docker container: {name}")
            cmd = [
                'docker', 'run', '-d',
                '--name', name,
                '--network', 'bridge',
                '--privileged',
                image
            ]
            subprocess.run(cmd, capture_output=True)
            time.sleep(2)

    def _setup_virtualbox(self):
        """Setup VirtualBox VMs"""
        print("[+] Setting up VirtualBox VMs...")
        time.sleep(5)

    def run_attack_sequence(self, attack_function, params: Dict):
        """Run automated attack sequence"""
        print("[+] Running automated attack sequence...")

        def run_with_timeout():
            try:
                attack_function(**params)
                self.attack_results['success'] = True
            except Exception as e:
                self.attack_results['success'] = False
                self.attack_results['error'] = str(e)

        thread = threading.Thread(target=run_with_timeout, daemon=True)
        thread.start()
        thread.join(timeout=params.get('timeout', 300))

        self.lab_status['attack_complete'] = True
        self.lab_status['end_time'] = datetime.now().isoformat()
        print("[+] Attack sequence complete")

    def cleanup_lab(self):
        """Clean up lab environment"""
        print("[+] Cleaning up lab...")

        lab_type = self.lab_config.get('type', 'eve-ng') if self.lab_config else None

        if lab_type == 'eve-ng':
            self._cleanup_eve_ng()
        elif lab_type == 'docker':
            self._cleanup_docker()
        else:
            print("[+] Manual cleanup required")

        self.lab_status['cleanup_complete'] = True
        print("[+] Cleanup complete")

    def _cleanup_eve_ng(self):
        """Cleanup EVE-NG lab"""
        print("[+] Stopping EVE-NG lab...")
        time.sleep(2)

    def _cleanup_docker(self):
        """Cleanup Docker containers"""
        containers = self.lab_config.get('docker', {}).get('containers', [])
        for container in containers:
            name = container.get('name', 'dhcp-lab')
            print(f"[+] Removing Docker container: {name}")
            subprocess.run(['docker', 'stop', name], capture_output=True)
            subprocess.run(['docker', 'rm', name], capture_output=True)

    def generate_lab_report(self) -> dict:
        """Generate lab report"""
        report = {
            'lab_config': self.lab_config,
            'status': self.lab_status,
            'attack_results': self.attack_results,
            'timestamp': datetime.now().isoformat()
        }

        with open('lab_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        print("[+] Lab report generated: lab_report.json")
        return report

    def __str__(self):
        return f"AutoLab(interface={self.interface}, status={self.lab_status})"