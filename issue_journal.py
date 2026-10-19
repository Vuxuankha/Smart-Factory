"""Thread-safe, bounded-memory CSV journal for issues and verified skips."""
import csv
import json
import os
import sqlite3
import tempfile
import unicodedata
from contextlib import closing
import shutil
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

FIELDS = ('time', 'account', 'status', 'folder', 'uid', 'sender', 'recipients', 'subject', 'reason', 'path')


def safe_csv(value):
    if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')):
        return "'" + value
    return value


def vietnamese_sort_key(value):
    """Case/accent-insensitive grouping for Unicode sender and recipient names."""
    folded = unicodedata.normalize('NFD', str(value or '').casefold().replace('đ', 'd'))
    return ''.join(ch for ch in folded if unicodedata.category(ch) != 'Mn')


def make_sender_recipient_sorted_csv(source, output):
    """Disk-backed sorting: works with large mailboxes without loading all rows in RAM.

    Uses SQLite only as temporary sort storage; original audit CSV is untouched.
    """
    source, output = Path(source), Path(output)
    with tempfile.TemporaryDirectory(prefix='.email_sort_', dir=source.parent) as temporary:
        temp = Path(temporary)
        with closing(sqlite3.connect(temp / 'sort.sqlite3')) as db:
            db.execute('CREATE TABLE rows (sender TEXT, recipients TEXT, seq INTEGER, data TEXT)')
            with source.open('r', encoding='utf-8-sig', newline='') as inp:
                reader = csv.DictReader(inp)
                batch = []
                for seq, row in enumerate(reader):
                    batch.append((vietnamese_sort_key(row.get('sender')),
                                  vietnamese_sort_key(row.get('recipients')),
                                  seq, json.dumps(row, ensure_ascii=False)))
                    if len(batch) == 500:
                        db.executemany('INSERT INTO rows VALUES (?,?,?,?)', batch)
                        batch.clear()
                if batch:
                    db.executemany('INSERT INTO rows VALUES (?,?,?,?)', batch)
            with (temp / 'sorted.csv').open('w', encoding='utf-8-sig', newline='') as output_file:
                writer = csv.DictWriter(output_file, fieldnames=FIELDS, extrasaction='ignore')
                writer.writeheader()
                for (data,) in db.execute('SELECT data FROM rows ORDER BY sender, recipients, seq'):
                    writer.writerow(json.loads(data))
        os.replace(temp / 'sorted.csv', output)
    return output


class IssueJournal:
    def __init__(self, destination):
        root = Path(destination) / '_BAO_CAO_LOI'
        root.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        self.path = root / ('email_ket_qua_' + stamp + '_' + uuid.uuid4().hex[:8] + '.csv')
        self.file = self.path.open('w', encoding='utf-8-sig', newline='')
        self.writer = csv.DictWriter(self.file, fieldnames=FIELDS, extrasaction='ignore')
        self.writer.writeheader()
        self.lock = threading.Lock()
        self.count = 0
        self.closed = False
        self.sorted_path = self.path.parent / 'email_sap_xep_nguoi_gui_nguoi_nhan.csv'
        self.sort_error = None

    def add(self, record):
        with self.lock:
            self.writer.writerow({k: safe_csv(record.get(k, '')) for k in FIELDS})
            self.count += 1
            if self.count % 50 == 0:
                self.file.flush()

    def close(self):
        with self.lock:
            if not self.closed:
                self.file.flush()
                self.file.close()
                self.closed = True
                latest = self.path.parent / 'email_loi_bo_qua_moi_nhat.csv'
                # Copy only after closing, to preserve historical run files.
                shutil.copyfile(self.path, latest)
                try:
                    make_sender_recipient_sorted_csv(self.path, self.sorted_path)
                except (OSError, ValueError, sqlite3.Error) as exc:
                    self.sort_error = f'{type(exc).__name__}: {exc}'

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
