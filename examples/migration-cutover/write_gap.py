"""Expose the check-to-switch write gap and a one-process write boundary."""

import json
from pathlib import Path
import sqlite3
import tempfile
from threading import Event, Lock, Thread

from lab import cents, new_rows, old_rows, reconciles, transform


def seed(folder: Path):
    source, target, pointer = (folder / name for name in
                               ('source.sqlite', 'target.sqlite', 'selected.txt'))
    with sqlite3.connect(source) as db:
        db.execute('CREATE TABLE orders(id TEXT PRIMARY KEY,amount TEXT NOT NULL)')
        db.execute('INSERT INTO orders VALUES (?,?)', ('a', '12.99'))
    transform(source, target, cents)
    pointer.write_text(source.name)
    return source, target, pointer


def join(thread: Thread):
    thread.join(timeout=3)
    if thread.is_alive():
        raise RuntimeError('Local fixture thread did not finish')


def unsafe_check_then_switch(folder: Path):
    source, target, pointer = seed(folder)
    checked, resume = Event(), Event()
    errors = []

    def selector():
        try:
            if not reconciles(source, target):
                raise RuntimeError('Fixture should initially match')
            checked.set()
            if not resume.wait(3):
                raise RuntimeError('Write did not arrive during the fixture gap')
            pointer.write_text(target.name)
        except Exception as error:
            errors.append(error)

    thread = Thread(target=selector)
    thread.start()
    try:
        if not checked.wait(3):
            raise RuntimeError('Selector did not reach the checked state')
        with sqlite3.connect(source) as db:
            db.execute('INSERT INTO orders VALUES (?,?)', ('late', '3.50'))
    finally:
        resume.set()
        join(thread)
    if errors:
        raise errors[0]
    assert pointer.read_text() == target.name
    assert ('late', '3.50') in old_rows(source)
    assert ('late', 350) not in new_rows(target)
    return {'selected_target_with_missing_committed_source_order': True}


class LocalWriteBoundary:
    """One-process teaching contract; every fixture writer uses the same lock."""

    def __init__(self, source: Path, target: Path, pointer: Path):
        self.source, self.target, self.pointer = source, target, pointer
        self.lock = Lock()

    def submit(self, order_id: str, amount: str):
        with self.lock:
            name = self.pointer.read_text()
            if name not in {self.source.name, self.target.name}:
                raise ValueError('Unknown selected store')
            path = self.source if name == self.source.name else self.target
            value = amount if path == self.source else cents(amount)
            with sqlite3.connect(path) as db:
                db.execute('INSERT INTO orders VALUES (?,?)', (order_id, value))
            return name

    def cutover(self, checked: Event, resume: Event):
        with self.lock:
            if not reconciles(self.source, self.target):
                return False
            checked.set()
            if not resume.wait(3):
                raise RuntimeError('Fixture did not release cutover')
            self.pointer.write_text(self.target.name)
            return True


def controlled_switch(folder: Path):
    source, target, pointer = seed(folder)
    route = LocalWriteBoundary(source, target, pointer)
    checked, resume, attempting = Event(), Event(), Event()
    outcome = {}
    errors = []

    def switch():
        try:
            outcome['selected'] = route.cutover(checked, resume)
        except Exception as error:
            errors.append(error)

    def writer():
        try:
            attempting.set()
            outcome['writer_store'] = route.submit('late', '3.50')
        except Exception as error:
            errors.append(error)

    selector = Thread(target=switch)
    selector.start()
    try:
        if not checked.wait(3):
            raise RuntimeError('Controlled selector did not reach the checked state')
        client = Thread(target=writer)
        client.start()
        if not attempting.wait(3):
            raise RuntimeError('Writer did not attempt the controlled route')
    finally:
        resume.set()
        join(selector)
    join(client)
    if errors:
        raise errors[0]
    assert outcome == {'selected': True, 'writer_store': target.name}
    assert ('late', 350) in new_rows(target)
    assert ('late', '3.50') not in old_rows(source)
    return {'post_switch_writer_used_target': True,
            'scope': 'one-process shared lock and selected writer only; no independent client or distributed write fence'}


def run(folder: Path):
    unsafe = folder / 'unsafe'
    safe = folder / 'controlled'
    unsafe.mkdir()
    safe.mkdir()
    return {'unsafe': unsafe_check_then_switch(unsafe),
            'controlled': controlled_switch(safe)}


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='amplify-cutover-write-gap-') as temp:
        folder = Path(temp)
        result = run(folder)
    result['temporary_resources_removed'] = not folder.exists()
    assert result['temporary_resources_removed']
    print(json.dumps(result, sort_keys=True))
