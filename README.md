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


⚖️ Legal Notice
THIS SOFTWARE IS PROVIDED FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY.

⚠️ IMPORTANT LEGAL WARNINGS
Authorized Use Only

This tool may ONLY be used on:

Your own private networks

Networks where you have explicit written permission

Authorized penetration testing labs (EVE-NG, GNS3, etc.)

Educational environments under supervision

Unauthorized Use is ILLEGAL

Using this tool on networks you don't own or have permission to test is:

A violation of local and international laws

Considered a cybercrime in most jurisdictions

Subject to severe legal penalties including imprisonment

Commercial Use Prohibited

Selling this tool or any of its components is strictly forbidden

Using this tool for commercial purposes without explicit permission is prohibited

Monetizing attacks performed with this tool is illegal

No Warranty

This tool is provided "AS IS" without any warranty

The developer is NOT responsible for:

Any damage caused by using this tool

Any legal consequences of misuse

Any financial or reputational damage

Any data loss or security breaches

User Responsibility

You are SOLELY responsible for:

How you use this tool

Obtaining proper authorization

Complying with all applicable laws

Any consequences of your actions

Ethical Use Agreement

By downloading, installing, or using this tool, you agree to:

Use it ethically and responsibly

Never use it for malicious purposes

Respect others' privacy and property rights

Accept full legal responsibility for your actions

🚫 Prohibited Activities
The following are STRICTLY PROHIBITED:

Attacking any network without explicit permission

Using this tool for extortion, blackmail, or harassment

Selling or distributing this tool commercially

Removing or altering this legal notice

Using this tool for any illegal purpose

📜 Legal Compliance
Users must comply with all applicable laws including but not limited to:

Computer Fraud and Abuse Act (CFAA) - USA

General Data Protection Regulation (GDPR) - EU

Network and Information Systems Directive (NIS) - EU

Local cybercrime laws in your jurisdiction

International cybercrime treaties

📄 Copyright
Copyright © 2026 Youssef Zedan. All Rights Reserved.

All Rights Reserved
This software and its source code are the exclusive property of Youssef Zedan. Unauthorized copying, modification, distribution, or use of this software is strictly prohibited.

Intellectual Property
Code: All code is original work by Youssef Zedan

Design: Framework architecture and design are proprietary

Documentation: All documentation is copyrighted

Brand: "Z-Storm" name and logo are trademarks

Permissions
For permissions beyond the scope of this license, contact the developer:
