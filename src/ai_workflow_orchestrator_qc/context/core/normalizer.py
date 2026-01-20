def normalize_maintenance(records):
    return [
        {
            "type": r["maintenance_type"],
            "date": r["performed_on"].isoformat(),
            "notes": r["notes"]
        }
        for r in records if r.get("notes")
    ]


def normalize_operator_notes(records):
    return [
        r["note"]
        for r in records if r.get("note")
    ]
