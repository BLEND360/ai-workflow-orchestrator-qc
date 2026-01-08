"""
Test cases and usage examples for Quality Defect Event Ingestion API
"""

import requests
import json
from datetime import datetime, timedelta

# Base URL (adjust for your environment)
BASE_URL = "http://localhost:8000"

# ============================================================================
# EXAMPLE 1: Basic Defect Event Ingestion
# ============================================================================

def test_basic_ingestion():
    """Test basic defect event ingestion"""
    print("\n=== Test 1: Basic Ingestion ===")
    
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "location": {
            "facility": "Manufacturing Plant A",
            "line": "Assembly Line 3",
            "station": "QC Station 2"
        },
        "defect": {
            "defect_type": "Surface Scratch",
            "description": "Minor scratch detected on product surface during quality inspection",
            "severity": "medium",
            "category": "cosmetic"
        },
        "product": {
            "product_id": "PROD-12345",
            "batch_id": "BATCH-2024-001",
            "serial_number": "SN-98765",
            "sku": "SKU-ABC-123"
        },
        "status": "detected",
        "metadata": {
            "inspector_id": "INS-001",
            "shift": "day",
            "temperature": 22.5,
            "humidity": 45
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/defects/ingest", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

# ============================================================================
# EXAMPLE 2: Idempotency with Event ID
# ============================================================================

def test_idempotency():
    """Test idempotency using event_id"""
    print("\n=== Test 2: Idempotency Test ===")
    
    event_id = "EVENT-UNIQUE-12345"
    
    payload = {
        "event_id": event_id,
        "timestamp": datetime.utcnow().isoformat(),
        "location": {
            "facility": "Manufacturing Plant B",
            "line": "Line 1"
        },
        "defect": {
            "defect_type": "Dimensional Error",
            "description": "Part dimensions outside tolerance",
            "severity": "high",
            "category": "dimensional"
        },
        "product": {
            "product_id": "PROD-67890"
        }
    }
    
    # First submission
    print("\n--- First Submission ---")
    response1 = requests.post(f"{BASE_URL}/api/v1/defects/ingest", json=payload)
    print(f"Status: {response1.status_code}")
    print(f"Response: {json.dumps(response1.json(), indent=2)}")
    
    # Second submission (duplicate)
    print("\n--- Second Submission (Should be duplicate) ---")
    response2 = requests.post(f"{BASE_URL}/api/v1/defects/ingest", json=payload)
    print(f"Status: {response2.status_code}")
    print(f"Response: {json.dumps(response2.json(), indent=2)}")

# ============================================================================
# EXAMPLE 3: Duplicate Detection by Content Hash
# ============================================================================

def test_content_duplicate():
    """Test duplicate detection based on content hash"""
    print("\n=== Test 3: Content-Based Duplicate Detection ===")
    
    timestamp = datetime.utcnow().isoformat()
    
    # Same content, different metadata and no event_id
    payload1 = {
        "timestamp": timestamp,
        "location": {
            "facility": "Plant C",
            "line": "Line 5"
        },
        "defect": {
            "defect_type": "Color Mismatch",
            "description": "Product color does not match specification",
            "severity": "low",
            "category": "visual"
        },
        "product": {
            "product_id": "PROD-11111"
        },
        "metadata": {"inspector": "John"}
    }
    
    payload2 = {
        "timestamp": timestamp,
        "location": {
            "facility": "Plant C",
            "line": "Line 5"
        },
        "defect": {
            "defect_type": "Color Mismatch",
            "description": "Product color does not match specification",
            "severity": "low",
            "category": "visual"
        },
        "product": {
            "product_id": "PROD-11111"
        },
        "metadata": {"inspector": "Jane"}  # Different metadata
    }
    
    print("\n--- First Submission ---")
    response1 = requests.post(f"{BASE_URL}/api/v1/defects/ingest", json=payload1)
    print(f"Status: {response1.status_code}")
    print(f"Response: {json.dumps(response1.json(), indent=2)}")
    
    print("\n--- Second Submission (Same content, different metadata) ---")
    response2 = requests.post(f"{BASE_URL}/api/v1/defects/ingest", json=payload2)
    print(f"Status: {response2.status_code}")
    print(f"Response: {json.dumps(response2.json(), indent=2)}")

# ============================================================================
# EXAMPLE 4: Validation Errors
# ============================================================================

def test_validation_errors():
    """Test various validation errors"""
    print("\n=== Test 4: Validation Errors ===")
    
    # Invalid timestamp (future)
    print("\n--- Test 4a: Future Timestamp ---")
    payload = {
        "timestamp": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "location": {"facility": "Plant D"},
        "defect": {
            "defect_type": "Test",
            "description": "Test defect",
            "severity": "low",
            "category": "test"
        },
        "product": {"product_id": "PROD-TEST"}
    }
    response = requests.post(f"{BASE_URL}/api/v1/defects/ingest", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Invalid severity
    print("\n--- Test 4b: Invalid Severity ---")
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "location": {"facility": "Plant D"},
        "defect": {
            "defect_type": "Test",
            "description": "Test defect",
            "severity": "super_critical",  # Invalid
            "category": "test"
        },
        "product": {"product_id": "PROD-TEST"}
    }
    response = requests.post(f"{BASE_URL}/api/v1/defects/ingest", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

# ============================================================================
# EXAMPLE 5: Critical Defect with Full Details
# ============================================================================

def test_critical_defect():
    """Test critical defect with all optional fields"""
    print("\n=== Test 5: Critical Defect ===")
    
    payload = {
        "event_id": "CRITICAL-EVENT-001",
        "timestamp": datetime.utcnow().isoformat(),
        "location": {
            "facility": "Manufacturing Plant A",
            "line": "Critical Assembly Line",
            "station": "Final Inspection",
            "coordinates": {"lat": 37.7749, "lon": -122.4194}
        },
        "defect": {
            "defect_type": "Structural Failure",
            "description": "Critical structural component shows signs of material fatigue",
            "severity": "critical",
            "category": "structural",
            "root_cause": "Material quality issue from supplier batch XYZ-789"
        },
        "product": {
            "product_id": "PROD-CRITICAL-999",
            "batch_id": "BATCH-2024-CRITICAL",
            "serial_number": "SN-CRITICAL-001",
            "sku": "SKU-SAFETY-001"
        },
        "status": "investigating",
        "metadata": {
            "inspector_id": "INS-SENIOR-001",
            "shift": "night",
            "reported_by": "Quality Manager",
            "severity_escalated": True,
            "requires_immediate_action": True,
            "affected_units_count": 150,
            "containment_actions": ["Line stopped", "Batch quarantined"]
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/defects/ingest",
        json=payload,
        headers={"X-Request-Id": "REQ-CRITICAL-001"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Check status
    if response.status_code in [200, 201]:
        correlation_id = response.json()["correlation_id"]
        print(f"\n--- Checking Event Status ---")
        status_response = requests.get(
            f"{BASE_URL}/api/v1/defects/status/{correlation_id}"
        )
        print(f"Status: {status_response.status_code}")
        print(f"Response: {json.dumps(status_response.json(), indent=2)}")

# ============================================================================
# EXAMPLE 6: Health Check
# ============================================================================

def test_health_check():
    """Test health check endpoint"""
    print("\n=== Test 6: Health Check ===")
    
    response = requests.get(f"{BASE_URL}/api/v1/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Quality Defect Event Ingestion API - Test Suite")
    print("=" * 80)
    
    try:
        # Check if API is running
        response = requests.get(f"{BASE_URL}/api/v1/health")
        if response.status_code != 200:
            print(f"\n❌ API is not responding properly at {BASE_URL}")
            print("Please start the API first using: uvicorn main:app --reload")
            exit(1)
        
        print("\n✅ API is running")
        
        # Run tests
        test_health_check()
        test_basic_ingestion()
        test_idempotency()
        test_content_duplicate()
        test_validation_errors()
        test_critical_defect()
        
        print("\n" + "=" * 80)
        print("All tests completed!")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to API at {BASE_URL}")
        print("Please start the API first using: uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ Error running tests: {str(e)}")