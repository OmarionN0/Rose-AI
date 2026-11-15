# Local telemetry retention

Real telemetry can include sensitive operational data. Default policy suggestion: keep only the minimum necessary for lab exercises.

The retention utility **does nothing destructive by default**. From `soc-lab/`:

```bash
python3 tools/retention.py --days 30
```

To actually delete expired events and associated alerts, first back up the local database to a private, access-controlled location, then run:

```bash
python3 tools/retention.py --days 30 --apply
```

Do not upload the database or reports to GitHub. SQLite WAL files may exist while the server is running. Stop the server before backing up or use SQLite's backup API to get a consistent copy. The utility is manual; there is no scheduled deletion service yet.
