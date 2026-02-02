from datetime import timedelta


class MockOperatorNotesRepository:

    def fetch(self, machine_id, window, limit):
        return [
            {
                "note": "Minor surface scratches observed intermittently",
                "created_at": window["to"] - timedelta(hours=6)
            }
        ][:limit]
