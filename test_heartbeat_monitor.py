#!/usr/bin/env python3
"""
Test cases for the Heartbeat Monitoring System
"""

import unittest
from datetime import datetime
from main import HeartbeatMonitor


class TestHeartbeatMonitor(unittest.TestCase):
    """Test cases for HeartbeatMonitor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = HeartbeatMonitor(expected_interval_seconds=60, allowed_misses=3)
    
    def test_working_alert_case(self):
        """Test case where a service misses 3 consecutive heartbeats and triggers an alert"""
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:01:00Z"},
            # Missing heartbeats at 10:02, 10:03, 10:04 (3 misses)
            {"service": "email", "timestamp": "2025-08-04T10:05:00Z"},
        ]
        
        alerts = self.monitor.monitor_heartbeats(events)
        
        # Should trigger an alert after missing 3 consecutive heartbeats
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['service'], 'email')
        # Alert should be at 10:04:00Z (after 3rd miss)
        self.assertEqual(alerts[0]['alert_at'], '2025-08-04T10:04:00Z')
    
    def test_near_miss_case(self):
        """Test case where a service misses only 2 heartbeats (no alert)"""
        events = [
            {"service": "sms", "timestamp": "2025-08-04T10:00:00Z"},
            # Missing heartbeats at 10:01, 10:02 (only 2 misses)
            {"service": "sms", "timestamp": "2025-08-04T10:03:00Z"},
        ]
        
        alerts = self.monitor.monitor_heartbeats(events)
        
        # Should NOT trigger an alert (only 2 misses)
        self.assertEqual(len(alerts), 0)
    
    def test_unordered_input(self):
        """Test that the system can handle unordered heartbeat events"""
        events = [
            {"service": "push", "timestamp": "2025-08-04T10:05:00Z"},
            {"service": "push", "timestamp": "2025-08-04T10:00:00Z"},  # Out of order
            {"service": "push", "timestamp": "2025-08-04T10:01:00Z"},  # Out of order
            # Missing heartbeats at 10:02, 10:03, 10:04 (3 misses)
        ]
        
        alerts = self.monitor.monitor_heartbeats(events)
        
        # Should still trigger an alert after sorting
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['service'], 'push')
        self.assertEqual(alerts[0]['alert_at'], '2025-08-04T10:04:00Z')
    
    def test_malformed_events(self):
        """Test handling of malformed events (missing fields, invalid timestamps)"""
        events = [
            {"service": "test", "timestamp": "2025-08-04T10:00:00Z"},  # Valid
            {"service": "test"},  # Missing timestamp
            {"timestamp": "2025-08-04T10:01:00Z"},  # Missing service
            {"service": "test", "timestamp": "not-a-timestamp"},  # Invalid timestamp
            {"service": "test", "timestamp": "2025-08-04T10:02:00Z"},  # Valid
            {},  # Empty object
            "not-a-dict",  # Not even a dictionary
        ]
        
        # Should process only valid events without crashing
        alerts = self.monitor.monitor_heartbeats(events)
        
        # No alert should be triggered (only 2 valid events)
        self.assertEqual(len(alerts), 0)
    
    def test_timestamp_parsing(self):
        """Test timestamp parsing functionality"""
        # Valid timestamp
        ts1 = self.monitor.parse_timestamp("2025-08-04T10:00:00Z")
        self.assertIsInstance(ts1, datetime)
        
        # Invalid timestamp
        ts2 = self.monitor.parse_timestamp("not-a-timestamp")
        self.assertIsNone(ts2)
        
        # Missing timestamp
        ts3 = self.monitor.parse_timestamp(None)
        self.assertIsNone(ts3)
    
    def test_event_validation(self):
        """Test event validation functionality"""
        # Valid event
        valid_event = {"service": "test", "timestamp": "2025-08-04T10:00:00Z"}
        self.assertTrue(self.monitor.validate_event(valid_event))
        
        # Missing service
        invalid_event1 = {"timestamp": "2025-08-04T10:00:00Z"}
        self.assertFalse(self.monitor.validate_event(invalid_event1))
        
        # Missing timestamp
        invalid_event2 = {"service": "test"}
        self.assertFalse(self.monitor.validate_event(invalid_event2))
        
        # Invalid timestamp
        invalid_event3 = {"service": "test", "timestamp": "invalid"}
        self.assertFalse(self.monitor.validate_event(invalid_event3))
        
        # Empty service
        invalid_event4 = {"service": "", "timestamp": "2025-08-04T10:00:00Z"}
        self.assertFalse(self.monitor.validate_event(invalid_event4))
        
        # Not a dictionary
        self.assertFalse(self.monitor.validate_event("not-a-dict"))
    
    def test_multiple_services(self):
        """Test monitoring multiple services simultaneously"""
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "sms", "timestamp": "2025-08-04T10:00:00Z"},
            # email misses 3 heartbeats at 10:01, 10:02, 10:03
            {"service": "email", "timestamp": "2025-08-04T10:04:00Z"},
            # sms continues normally
            {"service": "sms", "timestamp": "2025-08-04T10:01:00Z"},
            {"service": "sms", "timestamp": "2025-08-04T10:02:00Z"},
        ]
        
        alerts = self.monitor.monitor_heartbeats(events)
        
        # Only email should trigger an alert
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['service'], 'email')
        self.assertEqual(alerts[0]['alert_at'], '2025-08-04T10:03:00Z')
    
    def test_custom_parameters(self):
        """Test with custom interval and allowed misses"""
        monitor = HeartbeatMonitor(expected_interval_seconds=30, allowed_misses=2)
        
        events = [
            {"service": "test", "timestamp": "2025-08-04T10:00:00Z"},
            # Missing heartbeats at 10:00:30 and 10:01:00 (2 misses)
            {"service": "test", "timestamp": "2025-08-04T10:01:30Z"},
        ]
        
        alerts = monitor.monitor_heartbeats(events)
        
        # Should trigger alert after 2 misses
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['alert_at'], '2025-08-04T10:01:00Z')
    
    def test_recovery_after_alert(self):
        """Test that service can recover after triggering an alert"""
        events = [
            {"service": "test", "timestamp": "2025-08-04T10:00:00Z"},
            # Missing 3 heartbeats - triggers alert
            {"service": "test", "timestamp": "2025-08-04T10:04:00Z"},
            # Service recovers
            {"service": "test", "timestamp": "2025-08-04T10:05:00Z"},
            {"service": "test", "timestamp": "2025-08-04T10:06:00Z"},
        ]
        
        alerts = self.monitor.monitor_heartbeats(events)
        
        # Should only have one alert
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['alert_at'], '2025-08-04T10:03:00Z')


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)