/** Observe static entry transfers in an isolated local Chrome tab.
 *
 * This is a localhost measurement under this lab's cache/compression policy.
 * It is not an Amplify CDN observation or an AWS bill.
 */
import { createServer } from 'node:http';
import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { mkdtemp, readFile, realpath, rm, stat } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { extname, join, relative, resolve, sep } from 'node:path';
import { setTimeout as pause } from 'node:timers/promises';
import { gzipSync } from 'node:zlib';

const types = {
  '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript',
  '.svg': 'image/svg+xml', '.json': 'application/json', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.woff2': 'font/woff2',
};
const compressible = new Set(['.html', '.css', '.js', '.svg', '.json']);

function options(argv) {
  const result = { chrome: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' };
  for (let index = 0; index < argv.length; index += 2) {
    if (!['--dist', '--chrome'].includes(argv[index]) || !argv[index + 1]) {
      throw new Error('Usage: node browser_transfer_probe.mjs --dist PATH [--chrome PATH]');
    }
    result[argv[index].slice(2)] = argv[index + 1];
  }
  if (!result.dist) throw new Error('A local --dist directory is required');
  return result;
}

async function staticServer(root) {
  const hits = [];
  const server = createServer(async (request, response) => {
    try {
      if (request.method !== 'GET') {
        response.writeHead(405).end();
        return;
      }
      const pathname = new URL(request.url, 'http://localhost').pathname;
      const name = decodeURIComponent(pathname === '/' ? '/index.html' : pathname).slice(1);
      const candidate = resolve(root, name);
      if (!name || !candidate.startsWith(root + sep)) {
        response.writeHead(400).end();
        return;
      }
      const file = await realpath(candidate);
      if (!file.startsWith(root + sep) || !(await stat(file)).isFile()) {
        response.writeHead(404).end();
        return;
      }
      const raw = await readFile(file);
      const extension = extname(file).toLowerCase();
      const gzip = compressible.has(extension) && /\bgzip\b/.test(request.headers['accept-encoding'] || '');
      const body = gzip ? gzipSync(raw, { mtime: 0 }) : raw;
      const etag = '"' + createHash('sha256').update(raw).digest('hex') + '"';
      const cache = name === 'index.html' ? 'no-cache' : 'public, max-age=3600';
      const headers = {
        'Content-Type': (types[extension] || 'application/octet-stream') + (compressible.has(extension) ? '; charset=utf-8' : ''),
        'Cache-Control': cache, ETag: etag,
      };
      if (request.headers['if-none-match'] === etag) {
        response.writeHead(304, headers).end();
        hits.push({ path: name, status: 304, body_bytes: 0 });
        return;
      }
      if (gzip) headers['Content-Encoding'] = 'gzip';
      headers['Content-Length'] = body.length;
      response.writeHead(200, headers).end(body);
      hits.push({ path: name, status: 200, body_bytes: body.length, raw_file_bytes: raw.length });
    } catch {
      response.writeHead(404).end();
    }
  });
  await new Promise((done) => server.listen(0, '127.0.0.1', done));
  return { server, hits, origin: 'http://127.0.0.1:' + server.address().port };
}

class Cdp {
  constructor(socket) {
    this.socket = socket;
    this.next = 0;
    this.pending = new Map();
    this.listeners = new Map();
    socket.addEventListener('message', (message) => {
      const payload = JSON.parse(message.data);
      if (payload.id) {
        const waiter = this.pending.get(payload.id);
        this.pending.delete(payload.id);
        if (payload.error) waiter.reject(new Error(payload.error.message));
        else waiter.resolve(payload.result);
      } else {
        for (const listener of this.listeners.get(payload.method) || []) listener(payload);
      }
    });
  }
  send(method, params = {}, sessionId) {
    const id = ++this.next;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.socket.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
    });
  }
  on(method, listener) {
    const set = this.listeners.get(method) || new Set();
    set.add(listener);
    this.listeners.set(method, set);
    return () => set.delete(listener);
  }
  event(method, sessionId, timeout = 15000) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { off(); reject(new Error('Timed out waiting for ' + method)); }, timeout);
      const off = this.on(method, (message) => {
        if (message.sessionId !== sessionId) return;
        clearTimeout(timer);
        off();
        resolve(message.params);
      });
    });
  }
}

async function chromeConnection(chrome, userData) {
  const child = spawn(chrome, [
    '--headless=new', '--disable-gpu', '--disable-background-networking',
    '--no-first-run', '--no-default-browser-check', '--remote-debugging-port=0',
    '--proxy-server=http=127.0.0.1:9;https=127.0.0.1:9',
    '--proxy-bypass-list=127.0.0.1;localhost',
    '--user-data-dir=' + userData, 'about:blank',
  ], { stdio: 'ignore' });
  const portFile = join(userData, 'DevToolsActivePort');
  let port;
  for (let attempt = 0; attempt < 100; attempt++) {
    if (child.exitCode !== null) throw new Error('Chrome exited before DevTools started');
    try {
      port = Number((await readFile(portFile, 'utf8')).split('\n')[0]);
      if (port) break;
    } catch { /* Chrome is still starting. */ }
    await pause(100);
  }
  if (!port) throw new Error('Chrome DevTools did not start');
  const version = await (await fetch('http://127.0.0.1:' + port + '/json/version')).json();
  const socket = new WebSocket(version.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, { once: true });
    socket.addEventListener('error', reject, { once: true });
  });
  return { child, socket, cdp: new Cdp(socket) };
}

function visitSummary(hits, events) {
  return {
    local_requests: hits.length,
    response_body_bytes: hits.reduce((sum, hit) => sum + hit.body_bytes, 0),
    cached_requests: events.cached,
    blocked_nonlocal_requests: events.blocked,
    files: hits,
  };
}

async function main() {
  const { dist, chrome } = options(process.argv.slice(2));
  const root = await realpath(resolve(dist));
  if (!(await stat(join(root, 'index.html'))).isFile()) throw new Error('dist needs index.html');
  const userData = await mkdtemp(join(tmpdir(), 'amplify-transfer-chrome-'));
  const local = await staticServer(root);
  let browser;
  try {
    browser = await chromeConnection(chrome, userData);
    const { cdp } = browser;
    const { targetId } = await cdp.send('Target.createTarget', { url: 'about:blank' });
    const { sessionId } = await cdp.send('Target.attachToTarget', { targetId, flatten: true });
    await cdp.send('Page.enable', {}, sessionId);
    await cdp.send('Network.enable', {}, sessionId);
    await cdp.send('Network.setCacheDisabled', { cacheDisabled: false }, sessionId);
    await cdp.send('Fetch.enable', { patterns: [{ urlPattern: '*', requestStage: 'Request' }] }, sessionId);
    const events = { cached: 0, blocked: 0 };
    const offCache = cdp.on('Network.requestServedFromCache', (message) => {
      if (message.sessionId === sessionId) events.cached++;
    });
    const offFetch = cdp.on('Fetch.requestPaused', (message) => {
      if (message.sessionId !== sessionId) return;
      const { requestId, request } = message.params;
      const method = request.url.startsWith(local.origin + '/') ? 'Fetch.continueRequest' : 'Fetch.failRequest';
      if (method === 'Fetch.failRequest') events.blocked++;
      cdp.send(method, method === 'Fetch.failRequest'
        ? { requestId, errorReason: 'BlockedByClient' } : { requestId }, sessionId).catch(() => {});
    });
    const loaded = cdp.event('Page.loadEventFired', sessionId);
    await cdp.send('Page.navigate', { url: local.origin + '/' }, sessionId);
    await loaded;
    await pause(300);
    const first = visitSummary(local.hits.splice(0), { ...events });
    events.cached = 0;
    events.blocked = 0;
    const reloaded = cdp.event('Page.loadEventFired', sessionId);
    await cdp.send('Page.reload', { ignoreCache: false }, sessionId);
    await reloaded;
    await pause(300);
    const repeat = visitSummary(local.hits.splice(0), events);
    offCache();
    offFetch();
    console.log(JSON.stringify({
      scope: 'Local Chrome static entry with a temporary profile, blocked external requests, local gzip and cache policy; not AWS CDN or API transfer',
      dist: relative(process.cwd(), root), first, repeat,
    }, null, 2));
  } finally {
    browser?.socket.close();
    if (browser?.child.exitCode === null) {
      const exited = new Promise((done) => browser.child.once('exit', done));
      browser.child.kill();
      await Promise.race([exited, pause(3000)]);
    }
    await new Promise((done) => local.server.close(done));
    await rm(userData, { recursive: true, force: true, maxRetries: 8, retryDelay: 100 });
  }
}

main().catch((error) => { console.error('Local transfer probe stopped: ' + error.message); process.exitCode = 2; });
