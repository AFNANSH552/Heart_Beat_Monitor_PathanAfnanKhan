#!/usr/bin/env python3
"""
Heartbeat Monitoring System
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import argparse


class HeartbeatMonitor:
    def __init__(self, expected_interval_seconds: int = 60, allowed_misses: int = 3):
        self.expected_interval_seconds = expected_interval_seconds
        self.allowed_misses = allowed_misses

    def parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        if not isinstance(timestamp_str, str):
            return None
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except (ValueError, TypeError, AttributeError):
            return None

    def validate_event(self, event: Dict[str, Any]) -> bool:
        if not isinstance(event, dict):
            return False
        if 'service' not in event or not event['service']:
            return False
        if 'timestamp' not in event:
            return False
        return self.parse_timestamp(event['timestamp']) is not None

    def sort_events_by_service(self, events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        service_events = {}
        for event in events:
            if not self.validate_event(event):
                continue
            service = event['service']
            if service not in service_events:
                service_events[service] = []
            event_copy = event.copy()
            event_copy['parsed_timestamp'] = self.parse_timestamp(event['timestamp'])
            service_events[service].append(event_copy)
        for service in service_events:
            service_events[service].sort(key=lambda x: x['parsed_timestamp'])
        return service_events

    def detect_missed_heartbeats(self, service_events: List[Dict[str, Any]]) -> List[datetime]:
        if not service_events:
            return []

        alerts = []
        interval = timedelta(seconds=self.expected_interval_seconds)
        expected_time = service_events[0]['parsed_timestamp']
        event_index = 1
        consecutive_misses = 0

        while event_index < len(service_events):
            expected_time += interval
            actual_time = service_events[event_index]['parsed_timestamp']

            if actual_time <= expected_time:
                consecutive_misses = 0
                event_index += 1
            else:
                consecutive_misses += 1
                if consecutive_misses >= self.allowed_misses:
                    alerts.append(expected_time)
                    consecutive_misses = 0

        return alerts

    def monitor_heartbeats(self, events: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        service_events_map = self.sort_events_by_service(events)
        alerts = []
        for service, events_list in service_events_map.items():
            service_alerts = self.detect_missed_heartbeats(events_list)
            for alert_time in service_alerts:
                alerts.append({
                    'service': service,
                    'alert_at': alert_time.isoformat().replace('+00:00', 'Z')
                })
        return alerts


def load_events_from_file(filename: str) -> List[Dict[str, Any]]:
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading events from {filename}: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description='Monitor service heartbeats')
    parser.add_argument('--events-file', default='events.json',
                        help='JSON file containing heartbeat events')
    parser.add_argument('--interval', type=int, default=60,
                        help='Expected interval between heartbeats in seconds')
    parser.add_argument('--allowed-misses', type=int, default=3,
                        help='Number of consecutive misses before alert')
    parser.add_argument('--output-file', default='alerts.json',
                        help='File to store alerts output')

    args = parser.parse_args()
    events = load_events_from_file(args.events_file)
    if not events:
        print("No valid events found.")
        return

    monitor = HeartbeatMonitor(
        expected_interval_seconds=args.interval,
        allowed_misses=args.allowed_misses
    )
    alerts = monitor.monitor_heartbeats(events)

    # Print to console
    if alerts:
        print("Alerts triggered:")
        print(json.dumps(alerts, indent=2))
    else:
        print("No alerts triggered.")

    # Save to output file
    try:
        with open(args.output_file, "w") as outfile:
            json.dump(alerts, outfile, indent=2)
        print(f"Alerts saved to {args.output_file}")
    except Exception as e:
        print(f"Error saving alerts to {args.output_file}: {e}")


if __name__ == '__main__':
    main()
