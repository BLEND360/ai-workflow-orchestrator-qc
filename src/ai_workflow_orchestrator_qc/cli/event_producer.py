"""Mock event producer CLI for simulating defect events."""

import argparse
import random
import sys
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

import httpx

from ai_workflow_orchestrator_qc.api.models import DefectCategory, DefectSeverity


class DefectEventProducer:
    """Mock producer for generating and emitting defect events."""

    # Predefined defect types with realistic descriptions
    DEFECT_TYPES: Dict[str, Dict[str, str]] = {
        "vision": {
            "defect_type": "Image Quality Degradation",
            "description": "Detected image quality degradation in vision sensor feed. Blur detected in frame sequence.",
            "category": "DATA_QUALITY",
        },
        "sensor": {
            "defect_type": "Sensor Calibration Drift",
            "description": "Sensor calibration drift detected. Readings deviate from expected baseline.",
            "category": "FUNCTIONAL",
        },
        "data_validation": {
            "defect_type": "Data Validation Error",
            "description": "Invalid data format detected in incoming data stream. Schema validation failed.",
            "category": "DATA_QUALITY",
        },
        "performance": {
            "defect_type": "Response Time Degradation",
            "description": "API response time exceeded threshold. Latency spike detected in service calls.",
            "category": "PERFORMANCE",
        },
        "security": {
            "defect_type": "Unauthorized Access Attempt",
            "description": "Multiple unauthorized access attempts detected from suspicious IP addresses.",
            "category": "SECURITY",
        },
        "functional": {
            "defect_type": "Feature Malfunction",
            "description": "Critical feature malfunction detected. Expected functionality not working as designed.",
            "category": "FUNCTIONAL",
        },
        "usability": {
            "defect_type": "UI Rendering Issue",
            "description": "User interface rendering issue detected. Elements not displaying correctly.",
            "category": "USABILITY",
        },
        "compatibility": {
            "defect_type": "Browser Compatibility Issue",
            "description": "Compatibility issue detected with specific browser version. Feature not working.",
            "category": "COMPATIBILITY",
        },
        "network": {
            "defect_type": "Network Connectivity Issue",
            "description": "Network connectivity issues detected. Intermittent connection failures observed.",
            "category": "PERFORMANCE",
        },
        "database": {
            "defect_type": "Database Query Timeout",
            "description": "Database query timeout detected. Slow query performance impacting system.",
            "category": "PERFORMANCE",
        },
    }

    # Component names for different defect types
    COMPONENTS: Dict[str, List[str]] = {
        "vision": ["vision-sensor-01", "vision-sensor-02", "camera-feed-processor"],
        "sensor": ["temperature-sensor", "pressure-sensor", "motion-sensor"],
        "data_validation": ["data-ingestion-service", "data-pipeline", "etl-processor"],
        "performance": ["api-gateway", "user-service", "order-service"],
        "security": ["auth-service", "api-gateway", "edge-firewall"],
        "functional": ["payment-processor", "inventory-service", "notification-service"],
        "usability": ["frontend-app", "mobile-app", "admin-dashboard"],
        "compatibility": ["web-browser-client", "mobile-app", "desktop-app"],
        "network": ["load-balancer", "network-proxy", "cdn-edge"],
        "database": ["postgres-db", "mongodb-cluster", "redis-cache"],
    }

    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        severity: Optional[DefectSeverity] = None,
    ):
        """
        Initialize the defect event producer.

        Args:
            api_url: Base URL of the ingestion API
            severity: Default severity level (if None, will be randomly selected)
        """
        self.api_url = api_url.rstrip("/")
        self.default_severity = severity

    def generate_event(
        self,
        defect_type_key: Optional[str] = None,
        severity: Optional[DefectSeverity] = None,
        component: Optional[str] = None,
        event_id: Optional[str] = None,
        detected_by: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Generate a defect event.

        Args:
            defect_type_key: Key for defect type (if None, randomly selected)
            severity: Severity level (if None, uses default or random)
            component: Component name (if None, randomly selected based on defect type)
            event_id: Event ID (if None, auto-generated)
            detected_by: Who detected the defect (if None, auto-generated)
            metadata: Additional metadata

        Returns:
            Dictionary representing the defect event
        """
        # Select defect type
        if defect_type_key is None:
            defect_type_key = random.choice(list(self.DEFECT_TYPES.keys()))
        elif defect_type_key not in self.DEFECT_TYPES:
            raise ValueError(
                f"Unknown defect type: {defect_type_key}. "
                f"Available types: {', '.join(self.DEFECT_TYPES.keys())}"
            )

        defect_info = self.DEFECT_TYPES[defect_type_key]

        # Select severity
        if severity is None:
            if self.default_severity:
                severity = self.default_severity
            else:
                severity = random.choice(list(DefectSeverity))

        # Select component
        if component is None:
            available_components = self.COMPONENTS.get(
                defect_type_key, ["unknown-component"]
            )
            component = random.choice(available_components)

        # Generate event ID
        if event_id is None:
            event_id = f"defect-{datetime.now().strftime('%Y%m%d')}-{str(uuid4())[:8]}"

        # Generate detected_by
        if detected_by is None:
            detected_by = f"mock-producer-{random.choice(['sensor', 'vision', 'monitor'])}"

        # Prepare event
        event = {
            "event_id": event_id,
            "defect_type": defect_info["defect_type"],
            "severity": severity.value,
            "category": defect_info["category"],
            "description": defect_info["description"],
            "component": component,
            "detected_at": datetime.utcnow().isoformat() + "Z",
            "detected_by": detected_by,
            "metadata": metadata or {
                "source": "mock-producer",
                "defect_type_key": defect_type_key,
                "generated_at": datetime.utcnow().isoformat() + "Z",
            },
        }

        return event

    def emit_event(self, event: Dict) -> Dict:
        """
        Emit a defect event to the ingestion API.

        Args:
            event: The defect event dictionary

        Returns:
            Response from the API
        """
        url = f"{self.api_url}/api/v1/defects/ingest"
        try:
            response = httpx.post(url, json=event, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise RuntimeError(f"Failed to send event to API: {e}") from e
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"API returned error status {e.response.status_code}: {e.response.text}"
            ) from e


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Mock Event Producer - Emit defect events to the ingestion API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Emit a single random defect event
  python -m ai_workflow_orchestrator_qc.cli.event_producer emit

  # Emit a specific defect type with HIGH severity
  python -m ai_workflow_orchestrator_qc.cli.event_producer emit --type vision --severity HIGH

  # Emit 5 events of random types
  python -m ai_workflow_orchestrator_qc.cli.event_producer emit --count 5

  # List available defect types
  python -m ai_workflow_orchestrator_qc.cli.event_producer list-types

  # Emit with custom component and event ID
  python -m ai_workflow_orchestrator_qc.cli.event_producer emit --type sensor --component my-sensor --event-id custom-001
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.required = True

    # Emit command
    emit_parser = subparsers.add_parser(
        "emit", help="Emit defect event(s) to the ingestion API"
    )
    emit_parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Base URL of the ingestion API (default: http://localhost:8000)",
    )
    emit_parser.add_argument(
        "--type",
        dest="defect_type",
        choices=list(DefectEventProducer.DEFECT_TYPES.keys()),
        help="Type of defect to emit (if not specified, randomly selected)",
    )
    emit_parser.add_argument(
        "--severity",
        choices=[s.value for s in DefectSeverity],
        help="Severity level (if not specified, randomly selected)",
    )
    emit_parser.add_argument(
        "--category",
        choices=[c.value for c in DefectCategory],
        help="Override category (normally determined by defect type)",
    )
    emit_parser.add_argument(
        "--component",
        help="Component name (if not specified, randomly selected based on defect type)",
    )
    emit_parser.add_argument(
        "--event-id",
        help="Event ID (if not specified, auto-generated)",
    )
    emit_parser.add_argument(
        "--detected-by",
        help="Who detected the defect (if not specified, auto-generated)",
    )
    emit_parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of events to emit (default: 1)",
    )
    emit_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate event(s) but don't send to API (print to stdout)",
    )

    # List types command
    list_parser = subparsers.add_parser(
        "list-types", help="List available defect types"
    )

    args = parser.parse_args()

    if args.command == "list-types":
        print("Available defect types:")
        print("-" * 60)
        for key, info in DefectEventProducer.DEFECT_TYPES.items():
            print(f"\n{key}:")
            print(f"  Type: {info['defect_type']}")
            print(f"  Category: {info['category']}")
            print(f"  Description: {info['description']}")
        sys.exit(0)

    elif args.command == "emit":
        # Create producer
        severity = (
            DefectSeverity(args.severity) if args.severity else None
        )
        producer = DefectEventProducer(api_url=args.api_url, severity=severity)

        # Emit events
        success_count = 0
        for i in range(args.count):
            try:
                # Generate event
                event = producer.generate_event(
                    defect_type_key=args.defect_type,
                    severity=severity,
                    component=args.component,
                    event_id=args.event_id if args.count == 1 else None,
                    detected_by=args.detected_by,
                )

                # Override category if specified
                if args.category:
                    event["category"] = args.category

                if args.dry_run:
                    import json

                    print(f"Event {i+1}/{args.count}:")
                    print(json.dumps(event, indent=2))
                    print()
                else:
                    # Emit event
                    response = producer.emit_event(event)
                    success_count += 1
                    print(
                        f"✓ Event {i+1}/{args.count} emitted successfully: "
                        f"event_id={event['event_id']}, "
                        f"correlation_id={response.get('correlation_id')}, "
                        f"status={response.get('status')}"
                    )

            except Exception as e:
                print(f"✗ Failed to emit event {i+1}/{args.count}: {e}", file=sys.stderr)
                if args.count == 1:
                    sys.exit(1)

        if not args.dry_run:
            print(f"\n✓ Successfully emitted {success_count}/{args.count} event(s)")
            if success_count < args.count:
                sys.exit(1)


if __name__ == "__main__":
    main()

