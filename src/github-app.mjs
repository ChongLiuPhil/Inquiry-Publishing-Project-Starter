import { createPrivateKey, sign } from 'node:crypto';

export const WEBHOOK_PATH = '/_events/github';
const TARGET = 'ChongLiuPhil/Inquiry-Publishing-Project-Starter';
const MAX_BODY = 2 * 1024 * 1024;
const encoder = new TextEncoder();
const response = (status, message) => new Response(message, { status, headers: { 'Cache-Control': 'no-store', 'Content-Type': 'text/plain; charset=utf-8' } });

async function boundedBody(request) {
  if (Number(request.headers.get('content-length')) > MAX_BODY) throw new Error('size');
  if (!request.body) throw new Error('body');
  const reader = request.body.getReader();
  const chunks = [];
  let size = 0;
  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > MAX_BODY) { await reader.cancel(); throw new Error('size'); }
    chunks.push(value);
  }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  return bytes;
}

async function authenticated(body, signature, secret) {
  if (!/^sha256=[0-9a-f]{64}$/.test(signature || '')) return false;
  const bytes = Uint8Array.from(signature.slice(7).match(/../g), hex => parseInt(hex, 16));
  const key = await crypto.subtle.importKey('raw', encoder.encode(secret), {name:'HMAC', hash:'SHA-256'}, false, ['verify']);
  return crypto.subtle.verify('HMAC', key, bytes, body);
}

function privateKey(value) {
  // Secret editors may flatten PEM lines or preserve literal escaped newlines.
  const pem = String(value).replace(/\\r\\n|\\n|\\r/g, '\n').trim();
  const match = /^-----BEGIN (RSA PRIVATE KEY|PRIVATE KEY)-----([A-Za-z0-9+/=\s]+)-----END \1-----$/.exec(pem);
  if (!match) throw new Error('Invalid PEM');
  const body = match[2].replace(/\s/g, '');
  return createPrivateKey(`-----BEGIN ${match[1]}-----\n${body.match(/.{1,64}/g).join('\n')}\n-----END ${match[1]}-----\n`);
}

function appJWT(env) {
  const encode = value => Buffer.from(JSON.stringify(value)).toString('base64url');
  const now = Math.floor(Date.now() / 1000);
  const unsigned = `${encode({alg:'RS256', typ:'JWT'})}.${encode({iat:now-60, exp:now+300, iss:env.GITHUB_APP_ID})}`;
  // GitHub downloads PKCS#1 PEM; node:crypto also accepts PKCS#8.
  return `${unsigned}.${sign('RSA-SHA256', Buffer.from(unsigned), privateKey(env.GITHUB_APP_PRIVATE_KEY)).toString('base64url')}`;
}

export function makeHandler(registry, send = fetch) {
  return async (request, env) => {
    if (new URL(request.url).pathname !== WEBHOOK_PATH) return response(404, 'Not found');
    if (request.method !== 'POST') return response(405, 'POST required');
    if (!env.GITHUB_APP_WEBHOOK_SECRET || !env.GITHUB_APP_PRIVATE_KEY || !/^\d+$/.test(env.GITHUB_APP_ID || '')) {
      return response(503, 'GitHub App setup incomplete');
    }
    let body;
    try { body = await boundedBody(request); }
    catch { return response(413, 'Webhook body rejected; use manual source recovery'); }
    let stage = 'signature verification';
    try {
      if (!await authenticated(body, request.headers.get('x-hub-signature-256'), env.GITHUB_APP_WEBHOOK_SECRET)) return response(401, 'Invalid signature');
      const event = request.headers.get('x-github-event');
      if (event === 'ping') return response(200, 'Webhook signature verified');
      if (event !== 'push') return response(202, 'Event ignored');
      let payload;
      try { payload = JSON.parse(new TextDecoder().decode(body)); }
      catch { return response(400, 'Invalid payload'); }
      const repository = payload.repository?.full_name;
      // Starter's own pushes are handled by Workers Builds; never loop them back.
      if (repository === TARGET) return response(202, 'Starter push handled by Git integration');
      const source = registry.find(item => item.repository === repository);
      if (!source || payload.repository?.private !== false) return response(403, 'Source not registered for public publication');
      if (payload.deleted || payload.ref !== `refs/heads/${payload.repository?.default_branch}`) return response(202, 'Non-publication push ignored');
      if (payload.repository.default_branch !== source.branch) return response(409, 'Publication branch configuration drift');
      if (!/^[0-9a-f]{40}$/.test(payload.after || '') || !Number.isSafeInteger(payload.installation?.id) || payload.installation.id <= 0) return response(400, 'Invalid source identity');
      const headers = token => ({'Authorization':`Bearer ${token}`, 'Accept':'application/vnd.github+json', 'X-GitHub-Api-Version':'2022-11-28', 'User-Agent':'Inquiry-Publication-App', 'Content-Type':'application/json'});
      let jwt;
      try { jwt = appJWT(env); }
      catch { return response(502, 'GitHub App key signing failed; check the complete PEM secret'); }
      stage = 'installation token request';
      const minted = await send(`https://api.github.com/app/installations/${payload.installation.id}/access_tokens`, {
        method:'POST', headers:headers(jwt), signal:AbortSignal.timeout(3500),
        body:JSON.stringify({repositories:[TARGET.split('/')[1]], permissions:{actions:'write'}}),
      });
      if (minted.status !== 201) return response(502, 'GitHub App authentication failed; inspect installation permissions');
      const credentials = await minted.json();
      if (typeof credentials.token !== 'string' || !credentials.token) return response(502, 'GitHub App authentication failed');
      stage = 'Starter workflow dispatch';
      const dispatched = await send(`https://api.github.com/repos/${TARGET}/actions/workflows/refresh-public-site-sources.yml/dispatches`, {
        method:'POST', headers:headers(credentials.token), signal:AbortSignal.timeout(3500),
        body:JSON.stringify({ref:'main', inputs:{repository, branch:source.branch, revision:payload.after}}),
      });
      if (![200,204].includes(dispatched.status)) return response(502, 'Starter rejected the notification; redeliver after repair');
      return response(202, 'Starter accepted the notification; deployment remains subject to validation');
    } catch {
      // Never include JWTs, PEM, response bodies, webhook payloads or exceptions.
      return response(502, `Notification failed during ${stage}; redeliver after repair or run manual source recovery`);
    }
  };
}
