"""
IPFIX Simulator - Configuration-driven network traffic generator
Generates realistic IPFIX records for testing flow analytics systems
"""

import ipaddress
import json
import random
import socket
import struct
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import argparse
import yaml
import threading
import logging
import numpy as np
from scipy import stats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ipfix-simulator')


class IPFIXTemplate:
    """IPFIX Template definition"""
    def __init__(self, template_id: int, fields: List[Dict[str, Any]]):
        self.template_id = template_id
        self.fields = fields

    def to_bytes(self) -> bytes:
        """Convert template to binary format according to IPFIX spec"""
        # This is simplified - real implementation would follow RFC 7011
        # Build template header
        field_count = len(self.fields)
        template_header = struct.pack("!HH", self.template_id, field_count)

        # Build template fields
        template_fields = b''
        for field in self.fields:
            # Information Element ID and length
            template_fields += struct.pack("!HH",
                                         field['id'],
                                         field['length'])

        return template_header + template_fields

class IPFIXExporter:
    """IPFIX protocol exporter"""
    def __init__(self, export_ip: str, export_port: int, observation_domain_id: int = 1):
        self.export_ip = export_ip
        self.export_port = export_port
        self.observation_domain_id = observation_domain_id
        self.sequence_number = 0
        self.templates = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def add_template(self, template: IPFIXTemplate):
        """Register a template for use"""
        self.templates[template.template_id] = template

    def export_template(self, template_id: int):
        """Export a template to the collector"""
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")

        template = self.templates[template_id]
        # For text format, we don't need to export the template

    def export_data_record(self, template_id: int, data: Dict[str, Any]):
        """Export a data record using the specified template"""
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")

        template = self.templates[template_id]

        # Format data according to template
        record_data = []
        for field in template.fields:
            field_id = field['id']
            field_name = field.get('name', f"field_{field_id}")

            # Get value from data dict or use default
            value = data.get(field_name, 0)

            # Append field name and value to record data
            record_data.append(f"{field_name}: {value}")

        # Combine all parts into a text record
        text_record = ", ".join(record_data)

        # Print the text record (or you can write it to a file)
        print(text_record)
        logger.info(f"Exported data record using template {template_id}: {text_record}")


class TrafficProfile:
    """Defines a network traffic pattern"""
    def __init__(self, config: Dict[str, Any]):
        self.name = config['name']
        self.source_networks = config['source_networks']
        self.destination_networks = config['destination_networks']
        self.protocols = config['protocols']
        self.port_ranges = config['port_ranges']
        self.flow_size_distribution = config.get('flow_size_distribution', {
            'type': 'lognormal',
            'mean': 7.5,
            'sigma': 1.5
        })
        self.packet_size_distribution = config.get('packet_size_distribution', {
            'type': 'normal',
            'mean': 800,
            'sigma': 400,
            'min': 64,
            'max': 1500
        })
        self.flow_duration_distribution = config.get('flow_duration_distribution', {
            'type': 'lognormal',
            'mean': 8.0,
            'sigma': 1.2
        })
        self.time_pattern = config.get('time_pattern', {
            'type': 'constant',
            'flows_per_minute': 100
        })

    def generate_ip(self, network: str) -> str:
        """Generate a random IP within the specified network"""
        net = ipaddress.IPv4Network(network)
        # Generate random integer between network start and end
        random_int = random.randint(int(net.network_address), int(net.broadcast_address))
        return str(ipaddress.IPv4Address(random_int))

    def generate_flow(self, timestamp: int) -> Dict[str, Any]:
        """Generate a random flow based on this profile"""
        # Select random source and destination networks
        source_network = random.choice(self.source_networks)
        destination_network = random.choice(self.destination_networks)

        # Generate random IPs
        source_ip = self.generate_ip(source_network)
        destination_ip = self.generate_ip(destination_network)

        # Select protocol
        protocol = random.choice(self.protocols)

        # Generate ports based on protocol
        if protocol == 6 or protocol == 17:  # TCP or UDP
            source_port_range = self.port_ranges['source']
            dest_port_range = self.port_ranges['destination']
            source_port = random.randint(source_port_range[0], source_port_range[1])
            destination_port = random.randint(dest_port_range[0], dest_port_range[1])
        else:
            source_port = 0
            destination_port = 0

        # Generate flow size (bytes)
        if self.flow_size_distribution['type'] == 'lognormal':
            flow_size = int(np.random.lognormal(
                self.flow_size_distribution['mean'],
                self.flow_size_distribution['sigma']
            ))
        else:
            flow_size = random.randint(1000, 100000)

        # Generate packet count
        avg_packet_size = min(
            max(
                int(np.random.normal(
                    self.packet_size_distribution['mean'],
                    self.packet_size_distribution['sigma']
                )),
                self.packet_size_distribution['min']
            ),
            self.packet_size_distribution['max']
        )
        packet_count = max(1, int(flow_size / avg_packet_size))

        # Generate flow duration
        if self.flow_duration_distribution['type'] == 'lognormal':
            duration_ms = int(np.random.lognormal(
                self.flow_duration_distribution['mean'],
                self.flow_duration_distribution['sigma']
            ))
        else:
            duration_ms = random.randint(1, 60000)

        # Calculate flow start and end times
        flow_start_ms = timestamp * 1000
        flow_end_ms = flow_start_ms + duration_ms

        # Create flow record
        flow = {
            'sourceIPv4Address': source_ip,
            'destinationIPv4Address': destination_ip,
            'protocolIdentifier': protocol,
            'sourceTransportPort': source_port,
            'destinationTransportPort': destination_port,
            'octetDeltaCount': flow_size,
            'packetDeltaCount': packet_count,
            'flowStartMilliseconds': flow_start_ms,
            'flowEndMilliseconds': flow_end_ms
        }

        return flow

    def get_flow_rate(self, current_time: datetime) -> int:
        """Calculate flow rate based on time pattern"""
        base_rate = self.time_pattern.get('flows_per_minute', 100)

        # Apply pattern modifiers
        if self.time_pattern['type'] == 'constant':
            return base_rate

        elif self.time_pattern['type'] == 'diurnal':
            # Daily pattern with peak during working hours
            hour = current_time.hour
            # Simple bell curve centered at noon
            hour_factor = 0.5 + 0.5 * np.exp(-0.5 * ((hour - 12) / 4) ** 2)
            return int(base_rate * hour_factor)

        elif self.time_pattern['type'] == 'weekly':
            # Weekly pattern with weekdays having more traffic
            day_of_week = current_time.weekday()  # 0=Monday, 6=Sunday
            # Weekend factor
            if day_of_week >= 5:  # Weekend
                day_factor = 0.5
            else:  # Weekday
                day_factor = 1.0

            # Apply hourly pattern on top
            hour = current_time.hour
            hour_factor = 0.5 + 0.5 * np.exp(-0.5 * ((hour - 12) / 4) ** 2)

            return int(base_rate * day_factor * hour_factor)

        else:
            return base_rate


class AnomalyGenerator:
    """Generates network traffic anomalies"""
    def __init__(self, config: Dict[str, Any]):
        self.anomalies = config.get('anomalies', [])

    def get_active_anomalies(self, current_time: datetime) -> List[Dict[str, Any]]:
        """Return list of anomalies that should be active at the current time"""
        active = []

        for anomaly in self.anomalies:
            # Check if anomaly should be triggered
            start_time = datetime.fromisoformat(anomaly['start_time'])
            end_time = datetime.fromisoformat(anomaly['end_time'])

            if start_time <= current_time <= end_time:
                active.append(anomaly)

        return active

    def apply_anomalies(self, flows: List[Dict[str, Any]],
                         active_anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply active anomalies to a batch of flows"""
        if not active_anomalies:
            return flows

        modified_flows = flows.copy()

        for anomaly in active_anomalies:
            anomaly_type = anomaly['type']

            if anomaly_type == 'volumetric_ddos':
                # Volumetric DDoS attack - add many flows to a single destination
                target_ip = anomaly['target_ip']
                attack_flow_count = anomaly['flow_count']

                for _ in range(attack_flow_count):
                    # Create attack flow
                    attack_flow = {
                        'sourceIPv4Address': f"10.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
                        'destinationIPv4Address': target_ip,
                        'protocolIdentifier': random.choice([6, 17]),  # TCP or UDP
                        'sourceTransportPort': random.randint(1024, 65535),
                        'destinationTransportPort': anomaly.get('target_port', 80),
                        'octetDeltaCount': random.randint(60, 1500),
                        'packetDeltaCount': 1,
                        'flowStartMilliseconds': int(time.time() * 1000),
                        'flowEndMilliseconds': int(time.time() * 1000) + random.randint(1, 100)
                    }
                    modified_flows.append(attack_flow)

            elif anomaly_type == 'port_scan':
                # Port scan - single source scanning multiple ports on target
                source_ip = anomaly['source_ip']
                target_ip = anomaly['target_ip']
                port_count = anomaly['port_count']

                # Generate port scan flows
                for i in range(port_count):
                    scan_flow = {
                        'sourceIPv4Address': source_ip,
                        'destinationIPv4Address': target_ip,
                        'protocolIdentifier': 6,  # TCP
                        'sourceTransportPort': random.randint(1024, 65535),
                        'destinationTransportPort': i + 1,  # Sequential ports
                        'octetDeltaCount': random.randint(40, 100),
                        'packetDeltaCount': 1,
                        'flowStartMilliseconds': int(time.time() * 1000),
                        'flowEndMilliseconds': int(time.time() * 1000) + random.randint(1, 10)
                    }
                    modified_flows.append(scan_flow)

            elif anomaly_type == 'data_exfiltration':
                # Data exfiltration - large outbound flows to unusual destination
                source_ip = anomaly['source_ip']
                destination_ip = anomaly['destination_ip']

                # Create large outbound flow
                exfil_flow = {
                    'sourceIPv4Address': source_ip,
                    'destinationIPv4Address': destination_ip,
                    'protocolIdentifier': 6,  # TCP
                    'sourceTransportPort': random.randint(1024, 65535),
                    'destinationTransportPort': random.choice([22, 443, 8080]),
                    'octetDeltaCount': random.randint(10000000, 100000000),  # Very large
                    'packetDeltaCount': random.randint(7000, 70000),
                    'flowStartMilliseconds': int(time.time() * 1000),
                    'flowEndMilliseconds': int(time.time() * 1000) + random.randint(10000, 300000)
                }
                modified_flows.append(exfil_flow)

            elif anomaly_type == 'unusual_protocol':
                # Unusual protocol usage
                source_ip = anomaly['source_ip']
                destination_ip = anomaly['destination_ip']
                protocol = anomaly['protocol']

                # Create unusual protocol flow
                unusual_flow = {
                    'sourceIPv4Address': source_ip,
                    'destinationIPv4Address': destination_ip,
                    'protocolIdentifier': protocol,
                    'sourceTransportPort': random.randint(1024, 65535),
                    'destinationTransportPort': random.randint(1, 1024),
                    'octetDeltaCount': random.randint(100, 10000),
                    'packetDeltaCount': random.randint(1, 100),
                    'flowStartMilliseconds': int(time.time() * 1000),
                    'flowEndMilliseconds': int(time.time() * 1000) + random.randint(100, 10000)
                }
                modified_flows.append(unusual_flow)

        return modified_flows


class IPFIXSimulator:
    """Main simulator class"""
    def __init__(self, config_file: str):
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)

        # Set up exporter
        collector_ip = self.config['export']['collector_ip']
        collector_port = self.config['export']['collector_port']
        self.exporter = IPFIXExporter(collector_ip, collector_port)

        # Set up traffic profiles
        self.profiles = []
        for profile_config in self.config['traffic_profiles']:
            self.profiles.append(TrafficProfile(profile_config))

        # Set up anomaly generator
        self.anomaly_generator = AnomalyGenerator(self.config.get('anomalies', {}))

        # Set up template
        template_id = 256  # Standard templates use IDs < 256
        template_fields = [
            {'id': 8, 'length': 4, 'name': 'sourceIPv4Address'},
            {'id': 12, 'length': 4, 'name': 'destinationIPv4Address'},
            {'id': 7, 'length': 2, 'name': 'sourceTransportPort'},
            {'id': 11, 'length': 2, 'name': 'destinationTransportPort'},
            {'id': 4, 'length': 1, 'name': 'protocolIdentifier'},
            {'id': 1, 'length': 4, 'name': 'octetDeltaCount'},
            {'id': 2, 'length': 4, 'name': 'packetDeltaCount'},
            {'id': 152, 'length': 8, 'name': 'flowStartMilliseconds'},
            {'id': 153, 'length': 8, 'name': 'flowEndMilliseconds'}
        ]
        template = IPFIXTemplate(template_id, template_fields)
        self.exporter.add_template(template)
        self.template_id = template_id

        # Simulation parameters
        self.simulation_speed = self.config.get('simulation_speed', 1.0)
        self.start_time = datetime.fromisoformat(
            self.config.get('start_time', datetime.now().isoformat())
        )
        self.end_time = datetime.fromisoformat(
            self.config.get('end_time', (datetime.now() + timedelta(hours=1)).isoformat())
        )
        self.current_time = self.start_time
        self.running = False

    def start(self):
        """Start the simulation"""
        logger.info(f"Starting IPFIX simulation from {self.start_time} to {self.end_time}")
        logger.info(f"Exporting to {self.config['export']['collector_ip']}:{self.config['export']['collector_port']}")

        # Export template first
        self.exporter.export_template(self.template_id)

        self.running = True
        self.run_simulation()

    def stop(self):
        """Stop the simulation"""
        self.running = False
        logger.info("Simulation stopped")

    def run_simulation(self):
        """Run the simulation loop"""
        # Main simulation loop
        while self.running and self.current_time <= self.end_time:
            # Get active anomalies for current time
            active_anomalies = self.anomaly_generator.get_active_anomalies(self.current_time)
            if active_anomalies:
                logger.info(f"Active anomalies at {self.current_time}: {len(active_anomalies)}")

            # Generate flows for each profile
            all_flows = []
            for profile in self.profiles:
                # Calculate how many flows to generate
                flow_rate = profile.get_flow_rate(self.current_time)
                num_flows = max(1, int(flow_rate / 60))  # per second

                # Generate flows
                for _ in range(num_flows):
                    flow = profile.generate_flow(int(self.current_time.timestamp()))
                    all_flows.append(flow)

            # Apply anomalies
            all_flows = self.anomaly_generator.apply_anomalies(all_flows, active_anomalies)

            # Export flows
            for flow in all_flows:
                self.exporter.export_data_record(self.template_id, flow)

            # Update simulation time
            time_step = timedelta(seconds=1 * self.simulation_speed)
            self.current_time += time_step

            # Progress update
            if self.current_time.second % 10 == 0:
                progress = (self.current_time - self.start_time) / (self.end_time - self.start_time) * 100
                logger.info(f"Simulation progress: {progress:.1f}% - Current time: {self.current_time}")

            # Sleep to control simulation speed
            time.sleep(0.1 / self.simulation_speed)


def main():
    parser = argparse.ArgumentParser(description='IPFIX Traffic Simulator')
    parser.add_argument('--config', '-c', required=True, help='Configuration file path')
    args = parser.parse_args()

    simulator = IPFIXSimulator(args.config)

    try:
        simulator.start()
    except KeyboardInterrupt:
        logger.info("Simulation interrupted")
        simulator.stop()


if __name__ == "__main__":
    main()