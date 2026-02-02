from datetime import datetime, timedelta


class MockMaintenanceRepository:

    def fetch(self, machine_id, window, limit):
        return [
            {
                "maintenance_type": "calibration",
                "performed_on": window["to"] - timedelta(days=3),
                "notes": "Calibration drift detected"
            },
            {
                "maintenance_type": "part_replacement",
                "performed_on": window["to"] - timedelta(days=15),
                "notes": "Replaced polishing head"
            }
        ][:limit]
