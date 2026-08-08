#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Advanced Report Generator
Creates professional reports in multiple formats
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional


class AdvancedReport:
    """
    Advanced report generator for attack results
    """

    def __init__(self, attack_data: Dict, network_info: Dict = None):
        self.attack_data = attack_data
        self.network_info = network_info or {}
        self.timestamp = datetime.now().isoformat()
        self.report = {
            'meta': {
                'tool': 'Z-Storm',
                'version': '1.0.0',
                'timestamp': self.timestamp,
                'author': 'Yousef Zaidan'
            },
            'attack_summary': {},
            'statistics': {},
            'network_info': {},
            'recommendations': [],
            'logs': []
        }

    def generate(self, formats: List[str] = None) -> Dict[str, str]:
        """Generate report in multiple formats"""
        if formats is None:
            formats = ['json', 'html', 'markdown']

        self._build_report()
        results = {}

        for fmt in formats:
            if fmt == 'json':
                results['json'] = self._to_json()
            elif fmt == 'html':
                results['html'] = self._to_html()
            elif fmt == 'markdown':
                results['markdown'] = self._to_markdown()
            elif fmt == 'pdf':
                results['pdf'] = self._to_pdf()

        print(f"[+] Report generated in {len(results)} formats")
        return results

    def _build_report(self):
        """Build report content"""
        attack = self.attack_data.get('attack', {})
        stats = self.attack_data.get('stats', {})

        self.report['attack_summary'] = {
            'status': 'Success' if self.attack_data.get('success', False) else 'Failed',
            'mode': attack.get('mode', 'unknown'),
            'interface': attack.get('interface', 'unknown'),
            'threads': attack.get('threads', 0),
            'duration': f"{stats.get('total_attack_time', 0):.2f} seconds"
        }

        self.report['statistics'] = {
            'packets_sent': stats.get('packets_sent', 0),
            'macs_generated': stats.get('macs_generated', 0),
            'packets_per_second': stats.get('packets_per_second', 0),
            'total_packets': stats.get('packets_sent', 0),
            'success_rate': self._calculate_success_rate()
        }

        if self.network_info:
            self.report['network_info'] = {
                'interface': self.network_info.get('interface', 'unknown'),
                'gateway': self.network_info.get('gateway', 'unknown'),
                'total_hosts': self.network_info.get('total_hosts', 0),
                'dhcp_servers': self.network_info.get('dhcp_servers', [])
            }

        self.report['recommendations'] = self._generate_recommendations()
        self.report['logs'] = self._get_logs()

    def _calculate_success_rate(self) -> float:
        """Calculate success rate"""
        stats = self.attack_data.get('stats', {})
        packets = stats.get('packets_sent', 0)
        macs = stats.get('macs_generated', 0)

        if packets > 0:
            return (macs / packets) * 100
        return 0.0

    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations"""
        recommendations = [
            "Enable DHCP Snooping to prevent unauthorized DHCP servers",
            "Configure Port Security to limit MAC addresses per port",
            "Use dynamic ARP inspection (DAI) to prevent ARP spoofing",
            "Monitor network for unusual DHCP traffic patterns",
            "Implement network segmentation to limit attack scope",
            "Use 802.1X authentication for network access control"
        ]

        if self.attack_data.get('success', False):
            recommendations.append("Network vulnerable to DHCP Starvation attacks")
            recommendations.append("Implement DHCP server redundancy and monitoring")

        return recommendations

    def _get_logs(self) -> List[str]:
        """Get logs from file"""
        log_file = 'dhcp_attack.log'
        logs = []

        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    logs = lines[-20:]
            except:
                pass

        return logs

    def _to_json(self) -> str:
        """Generate JSON report"""
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)

        print(f"[+] JSON report: {filename}")
        return filename

    def _to_html(self) -> str:
        """Generate HTML report"""
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        stats = self.report['statistics']
        attack = self.report['attack_summary']

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Z-Storm Attack Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0e27;
            color: #e0e0e0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #141937;
            border-radius: 20px;
            padding: 30px;
            border: 1px solid #2a3a6a;
        }}
        .header {{
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 2px solid #2a3a6a;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.5em;
            color: #4a9eff;
            text-shadow: 0 0 20px rgba(74, 158, 255, 0.3);
        }}
        .header .subtitle {{
            color: #8899bb;
            font-size: 1.1em;
            margin-top: 5px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .card {{
            background: #1a2248;
            border-radius: 15px;
            padding: 20px;
            border: 1px solid #2a3a6a;
            transition: all 0.3s ease;
        }}
        .card:hover {{
            border-color: #4a9eff;
            transform: translateY(-2px);
        }}
        .card h3 {{
            color: #4a9eff;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        .card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #fff;
        }}
        .card .label {{
            color: #8899bb;
            font-size: 0.8em;
            margin-top: 5px;
        }}
        .status-success {{ color: #4ade80; }}
        .status-failed {{ color: #f87171; }}
        .section-title {{
            color: #4a9eff;
            font-size: 1.5em;
            margin: 30px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 1px solid #2a3a6a;
        }}
        .recommendations {{
            background: #1a2248;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
        }}
        .recommendations li {{
            padding: 8px 0;
            list-style: none;
            border-bottom: 1px solid #2a3a6a;
        }}
        .recommendations li:last-child {{
            border-bottom: none;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #2a3a6a;
            color: #667799;
            font-size: 0.9em;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .badge-success {{ background: #1a3a2a; color: #4ade80; }}
        .badge-failed {{ background: #3a1a1a; color: #f87171; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌩️ Z-Storm Report</h1>
            <div class="subtitle">Attack Analysis & Network Security Report</div>
            <div style="margin-top: 10px;">
                <span class="badge badge-{'success' if self.attack_data.get('success', False) else 'failed'}">
                    {'✅ SUCCESS' if self.attack_data.get('success', False) else '❌ FAILED'}
                </span>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>📦 Packets Sent</h3>
                <div class="value">{stats.get('packets_sent', 0)}</div>
                <div class="label">Total packets transmitted</div>
            </div>
            <div class="card">
                <h3>🔢 MACs Generated</h3>
                <div class="value">{stats.get('macs_generated', 0)}</div>
                <div class="label">Unique MAC addresses</div>
            </div>
            <div class="card">
                <h3>⚡ Packets/Sec</h3>
                <div class="value">{stats.get('packets_per_second', 0):.1f}</div>
                <div class="label">Average rate</div>
            </div>
            <div class="card">
                <h3>⏱️ Duration</h3>
                <div class="value">{attack.get('duration', '0s')}</div>
                <div class="label">Total attack time</div>
            </div>
        </div>

        <div class="section-title">📋 Attack Details</div>
        <div class="grid">
            <div class="card">
                <h3>🎯 Mode</h3>
                <div class="value" style="font-size: 1.2em;">{attack.get('mode', 'unknown')}</div>
            </div>
            <div class="card">
                <h3>🖥️ Interface</h3>
                <div class="value" style="font-size: 1.2em;">{attack.get('interface', 'unknown')}</div>
            </div>
            <div class="card">
                <h3>🧵 Threads</h3>
                <div class="value">{attack.get('threads', 0)}</div>
            </div>
            <div class="card">
                <h3>📊 Success Rate</h3>
                <div class="value">{stats.get('success_rate', 0):.1f}%</div>
            </div>
        </div>

        <div class="section-title">🛡️ Security Recommendations</div>
        <div class="recommendations">
            <ul>
                {''.join([f'<li>🔹 {rec}</li>' for rec in self.report.get('recommendations', [])])}
            </ul>
        </div>

        <div class="section-title">🌐 Network Information</div>
        <div class="grid">
            <div class="card">
                <h3>🚪 Gateway</h3>
                <div class="value" style="font-size: 1.1em;">{self.report.get('network_info', {}).get('gateway', 'unknown')}</div>
            </div>
            <div class="card">
                <h3>💻 Total Hosts</h3>
                <div class="value">{self.report.get('network_info', {}).get('total_hosts', 0)}</div>
            </div>
            <div class="card">
                <h3>📡 DHCP Servers</h3>
                <div class="value">{len(self.report.get('network_info', {}).get('dhcp_servers', []))}</div>
            </div>
        </div>

        <div class="footer">
            <p>Generated by Z-Storm v1.0.0</p>
            <p>Author: Youssef Zedan | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"[+] HTML report: {filename}")
        return filename

    def _to_markdown(self) -> str:
        """Generate Markdown report"""
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        md = f"""# 🌩️ Z-Storm Attack Report

## Summary
- **Status**: {'✅ SUCCESS' if self.attack_data.get('success', False) else '❌ FAILED'}
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Mode**: {self.report['attack_summary'].get('mode', 'unknown')}
- **Duration**: {self.report['attack_summary'].get('duration', '0s')}

## Statistics
| Metric | Value |
|--------|-------|
| Packets Sent | {self.report['statistics'].get('packets_sent', 0)} |
| MACs Generated | {self.report['statistics'].get('macs_generated', 0)} |
| Packets/Sec | {self.report['statistics'].get('packets_per_second', 0):.1f} |
| Success Rate | {self.report['statistics'].get('success_rate', 0):.1f}% |

## Network Information
- **Interface**: {self.report.get('network_info', {}).get('interface', 'unknown')}
- **Gateway**: {self.report.get('network_info', {}).get('gateway', 'unknown')}
- **Total Hosts**: {self.report.get('network_info', {}).get('total_hosts', 0)}
- **DHCP Servers**: {len(self.report.get('network_info', {}).get('dhcp_servers', []))}

## Security Recommendations
"""
        for rec in self.report.get('recommendations', []):
            md += f"- {rec}\n"

        md += f"""
---
*Generated by Z-Storm v1.0.0*
*Author: Yousef Zaidan*
"""

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(md)

        print(f"[+] Markdown report: {filename}")
        return filename

    def _to_pdf(self) -> str:
        """Generate PDF report (requires wkhtmltopdf)"""
        html_file = self._to_html()
        pdf_file = html_file.replace('.html', '.pdf')

        try:
            import subprocess
            result = subprocess.run(
                ['wkhtmltopdf', html_file, pdf_file],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"[+] PDF report: {pdf_file}")
                return pdf_file
            else:
                print("[!] wkhtmltopdf not found. Install: sudo apt install wkhtmltopdf")
                return html_file
        except:
            print("[!] PDF generation failed. Using HTML instead.")
            return html_file