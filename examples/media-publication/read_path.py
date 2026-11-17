"""Loopback visitor path for a synthetic publication; no object store or CDN."""
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sqlite3
from urllib.parse import urlsplit

from lab import digest


def current_manifest(db_path):
    with closing(sqlite3.connect(db_path)) as db:
        generation, revision, encoded = db.execute(
            'SELECT generation, revision, manifest FROM current'
        ).fetchone()
    return generation, revision, json.loads(encoded)


def visitor_server(db_path, objects, media_cache_control='no-store'):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path)
            if path.query or path.fragment:
                self.reply(404, {'error': 'not found'})
                return
            _, revision, manifest = current_manifest(db_path)
            if path.path == '/current':
                if not manifest:
                    self.reply(410, {'status': 'withdrawn'})
                    return
                self.reply(200, {
                    'revision': revision,
                    'variants': {name: '/media/' + item['key'].removeprefix('published/')
                                 for name, item in manifest['variants'].items()},
                })
                return
            if not manifest:
                self.reply(404, {'error': 'not found'})
                return
            for item in manifest['variants'].values():
                allowed_path = '/media/' + item['key'].removeprefix('published/')
                if path.path == allowed_path:
                    value = objects.get(item['key'])
                    if value is None or digest(value) != item['digest']:
                        self.reply(503, {'error': 'published bytes unavailable'})
                        return
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.send_header('Cache-Control', media_cache_control)
                    self.send_header('Content-Length', str(len(value)))
                    self.end_headers()
                    self.wfile.write(value)
                    return
            self.reply(404, {'error': 'not found'})

        def reply(self, status, body):
            encoded = json.dumps(body).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, *_args):
            pass

    return ThreadingHTTPServer(('127.0.0.1', 0), Handler)


def withdraw(db, expected_generation):
    """Remove the local visitor pointer; retain the revision floor."""
    db.execute('BEGIN IMMEDIATE')
    try:
        generation, revision = db.execute(
            'SELECT generation, revision FROM current'
        ).fetchone()
        if generation != expected_generation:
            db.rollback()
            return 'stale withdrawal'
        db.execute('UPDATE current SET generation=?, revision=?, manifest=?',
                   (generation + 1, revision, '{}'))
        db.commit()
        return 'withdrawn'
    except Exception:
        db.rollback()
        raise
