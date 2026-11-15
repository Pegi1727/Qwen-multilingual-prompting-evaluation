from pathlib import Path
import csv, hashlib
root = Path(__file__).resolve().parent
with (root/'MANIFEST_SHA256.csv').open(newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
for row in rows:
    p = root/row['path']
    assert p.is_file(), row['path']
    assert p.stat().st_size == int(row['bytes']), row['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256'], row['path']
print(f'PASS: {len(rows)} files verified.')
