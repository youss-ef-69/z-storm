# 🌩️ Z-Storm Framework

**Z-Storm** is an advanced network attack framework for penetration testing and lab automation, built with **Python** and **Scapy**. It's designed for security researchers, network engineers, and penetration testers to evaluate network security in authorized lab environments.

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/youss-ef-69/z-storm)

---

## 📋 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Attack Types](#-attack-types)
- [Usage Examples](#-usage-examples)
- [Command Line Options](#-command-line-options)
- [Project Structure](#-project-structure)
- [Reporting](#-reporting)
- [Disclaimer](#-disclaimer)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## ✨ Features

### Core Features
- **DHCP Starvation Attack** - Exhaust DHCP server IP addresses by sending thousands of DHCP Discover requests with spoofed MAC addresses
- **ARP Spoofing** - Perform Man-in-The-Middle (MITM) attacks by poisoning ARP tables
- **DTP Spoofing** - **NEW!** Spoof Switch roles by sending Dynamic Trunking Protocol (DTP) packets
- **Smart Scanner** - Intelligent network scanning with device classification (DHCP servers, routers, hosts)
- **Advanced Reporting** - Generate comprehensive reports in JSON, HTML, and Markdown formats

### Advanced Features
- **Multi-threaded Architecture** - High-performance parallel packet sending
- **Intelligent MAC Generation** - Uses real OUI (Organizationally Unique Identifier) prefixes
- **Stealth Mode** - Randomized delays and MAC spoofing for evasion
- **Lab Automation** - Integration with EVE-NG and GNS3
- **Comprehensive Logging** - Detailed logging with rotation support
- **YAML Configuration** - Easy customization without touching code

---

## 📦 Requirements

### System Requirements
- **Operating System:** Linux (Kali Linux recommended)
- **Python:** 3.6 or higher
- **Root Privileges:** Required for packet operations

### Python Dependencies

Legal Notice & Copyright
THIS SOFTWARE IS PROVIDED FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY.

Copyright © 2026 Youssef Zedan. All Rights Reserved.

This software and its source code are the exclusive property of Youssef Zedan. Unauthorized copying, modification, distribution, or use is strictly prohibited. "Z-Storm" name and logo are trademarks.

Important Legal Warnings
Authorized Use Only: This tool may ONLY be used on your own private networks, networks with explicit written permission, or authorized penetration testing labs

Unauthorized Use is ILLEGAL: Using this tool on networks you don't own or have permission to test is a violation of local and international laws, considered a cybercrime, and subject to severe legal penalties

Commercial Use Prohibited: Selling this tool or using it for commercial purposes is strictly forbidden

No Warranty: This tool is provided "AS IS" without any warranty. The developer is NOT responsible for any damage, legal consequences, or financial losses

User Responsibility: You are SOLELY responsible for how you use this tool, obtaining proper authorization, complying with all laws, and any consequences of your actions

Ethical Use Agreement: By using this tool, you agree to use it ethically, never for malicious purposes, respect privacy, and accept full legal responsibility

Prohibited Activities
Attacking any network without explicit permission

Using for extortion, blackmail, or harassment

Selling or distributing commercially

Removing or altering this legal notice

Using for any illegal purpose

Contact
GitHub: github.com/youss-ef-69

Repository: github.com/youss-ef-69/z-storm

Remember: With great power comes great responsibility. Use ethically and legally! 🌩️
