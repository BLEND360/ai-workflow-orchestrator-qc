class MockMetadataRepository:

    def fetch(self, machine_id):
        if machine_id != "M-102":
            raise ValueError("Machine metadata not found")

        return {
            "machine_id": "M-102",
            "model": "XJ-900",
            "installation_date": "2022-06-01",
            "operating_ranges": {
                "temperature": "10-80C",
                "speed": "100-300rpm"
            },
            "critical_components": [
                "polishing_head",
                "drive_motor"
            ]
        }
