# Heartbeat Monitoring System

A Python implementation of a heartbeat monitoring system that tracks service heartbeats and triggers alerts when services miss consecutive expected heartbeats.

## Overview

This system monitors service heartbeats and alerts when a service misses a specified number of consecutive expected heartbeats. It handles malformed data gracefully and can process events that arrive out of chronological order.

## Features

* **Robust Event Processing** : Handles malformed events (missing fields, invalid timestamps) without crashing
* **Chronological Sorting** : Automatically sorts events by timestamp per service
* **Configurable Parameters** : Customizable heartbeat interval and allowed misses
* **Multiple Service Support** : Monitors multiple services simultaneously
* **Comprehensive Testing** : Includes all required test cases plus additional edge cases

## Project Structure

```
├── main.py                    # Main heartbeat monitoring implementation
├── test_heartbeat_monitor.py  # Comprehensive test suite
├── events.json               # Sample heartbeat events data
├── README.md                 # This documentation
└── requirements.txt          # Python dependencies
```

## Installation & Setup

1. **Clone or download** the project files to your local machine
2. **Install dependencies** (optional, uses only standard library):
3. No external dependencies required
4. ```bash
   pip install -r requirements.txt
   ```
5. **Verify Python version** : Requires Python 3.6+

```bash
   python3 --version
```

## Usage

### Running the Main Solution

#### Basic Usage

```bash
python3 main.py
```

This will process the default `events.json` file with default parameters:

* Expected interval: 60 seconds
* Allowed misses: 3 consecutive misses

#### Custom Parameters

```bash
python3 main.py --interval 30 --allowed-misses 2 --events-file events.json
```

#### Command Line Options

* `--events-file`: Path to JSON file containing events (default: `events.json`)
* `--interval`: Expected interval between heartbeats in seconds (default: 60)
* `--allowed-misses`: Number of consecutive misses before alert (default: 3)
* --output-file `: Path to save the alerts output as JSON (default: `alerts.json`)

### Running Test Cases

#### Run All Tests

```bash
python3 test_heartbeat_monitor.py
```

#### Run Tests with Verbose Output

```bash
python3 -m unittest test_heartbeat_monitor.py -v
```

#### Run Specific Test

```bash
python3 -m unittest test_heartbeat_monitor.TestHeartbeatMonitor.test_working_alert_case
```

## Input Format

The system expects a JSON file containing an array of event objects:

```json
[
    {
        "service": "email",
        "timestamp": "2025-08-04T10:00:00Z"
    },
    {
        "service": "sms", 
        "timestamp": "2025-08-04T10:01:00Z"
    }
]
```

### Event Fields

* `service` (required): String identifier for the service
* `timestamp` (required): ISO format timestamp string

### Malformed Event Handling

The system gracefully handles:

* Missing `service` or `timestamp` fields
* Invalid timestamp formats
* Empty objects
* Non-dictionary items

## Output Format

The system outputs JSON array of alert objects:

```json
[
    {
        "service": "email",
        "alert_at": "2025-08-04T10:06:00Z"
    }
]
```

## Algorithm Details

### Heartbeat Detection Logic

1. **Event Validation** : Filter out malformed events
2. **Service Grouping** : Group events by service name
3. **Chronological Sorting** : Sort events per service by timestamp
4. **Miss Detection** : For each service:

* Start from first heartbeat
* Check for expected heartbeats at regular intervals
* Count consecutive misses
* Trigger alert when consecutive misses reach threshold
* Reset miss counter after alert

### Time Complexity

* **Sorting** : O(n log n) where n is number of events per service
* **Miss Detection** : O(m) where m is time span of monitoring
* **Overall** : O(n log n) for typical use cases

### Space Complexity

* O(n) for storing and processing events

## Test Cases Included

### Required Test Cases

1. **Working Alert Case** : Service misses 3 consecutive heartbeats → triggers alert
2. **Near-miss Case** : Service misses only 2 heartbeats → no alert
3. **Unordered Input** : Events arrive out of chronological order → system handles correctly
4. **Malformed Events** : Invalid/missing fields → system continues processing

### Additional Test Cases

5. **Timestamp Parsing** : Validates timestamp parsing edge cases
6. **Event Validation** : Tests all validation scenarios
7. **Multiple Services** : Multiple services monitored simultaneously
8. **Custom Parameters** : Different interval and miss thresholds
9. **Recovery After Alert** : Service recovery after triggering alert

## Example Usage with Provided Data

The provided `events.json` contains sample data with various services (email, sms, push). Running with default parameters:

```bash
python3 main.py
```

Will analyze the events and output any alerts triggered by services missing 3 consecutive expected heartbeats.

## Error Handling

The system includes comprehensive error handling:

* **File I/O** : Graceful handling of missing or invalid JSON files
* **Data Validation** : Skips malformed events without crashing
* **Timestamp Parsing** : Handles various invalid timestamp formats
* **Empty Data** : Handles empty event lists or missing services

## Dependencies

The project uses only Python standard library modules:

* `json`: JSON parsing
* `datetime`: Timestamp handling
* `argparse`: Command line argument parsing
* `unittest`: Testing framework

No external dependencies required!

## Development Notes

### Code Quality Features

* **Type Hints** : Full type annotation for better code clarity
* **Docstrings** : Comprehensive documentation for all functions
* **Error Handling** : Graceful handling of edge cases
* **Modularity** : Clean separation of concerns
* **Readability** : Clear variable names and logical structure

### Testing Philosophy

* **Comprehensive Coverage** : Tests cover all major functionality
* **Edge Cases** : Includes boundary and error conditions
* **Realistic Scenarios** : Tests mirror real-world usage patterns
* **Maintainability** : Tests are clear and well-documented

## License

This project is created for educational/assessment purposes.
