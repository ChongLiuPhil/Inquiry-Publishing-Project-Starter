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

// Signed bot pushes create PRs as the App, so ordinary PR CI can run.
async function openSourcePR(payload, env, registry, send) {
  const head = payload.after;
  const branch = `automation/site-sources-${head}`;
  if (payload.deleted || !/^[0-9a-f]{40}$/.test(head || '') || payload.ref !== `refs/heads/${branch}` ||
      payload.repository?.private !== false || payload.repository?.id !== 1377778633 ||
      !Number.isSafeInteger(payload.installation?.id) || payload.installation.id <= 0) {
    return response(400, 'Invalid source-update branch identity');
  }
  const headers = token => ({Authorization:`Bearer ${token}`, Accept:'application/vnd.github+json',
    'X-GitHub-Api-Version':'2022-11-28', 'User-Agent':'Inquiry-Publication-App', 'Content-Type':'application/json'});
  const minted = await send(`https://api.github.com/app/installations/${payload.installation.id}/access_tokens`, {
    method:'POST', headers:headers(appJWT(env)), signal:AbortSignal.timeout(3500),
    body:JSON.stringify({repositories:[TARGET.split('/')[1]], permissions:{contents:'read', pull_requests:'write'}}),
  });
  if (minted.status !== 201) return response(503, 'App requires approved Starter Pull requests write permission');
  const credentials = await minted.json();
  if (typeof credentials.token !== 'string' || !credentials.token) throw new Error('Token missing');
  const api = async (path, method='GET', body) => {
    const r = await send(`https://api.github.com/${path}`, {method,headers:headers(credentials.token),
      signal:AbortSignal.timeout(3500), ...(body ? {body:JSON.stringify(body)} : {})});
    if (!r.ok) throw new Error('GitHub operation failed');
    return r.json();
  };
  const comparison = await api(`repos/${TARGET}/compare/main...${head}`);
  if (comparison.status !== 'ahead' || comparison.ahead_by !== 1 || comparison.behind_by !== 0 ||
      comparison.files?.length !== 1 || comparison.files[0].filename !== 'site/sources.lock.json' ||
      comparison.files[0].status !== 'modified') return response(409, 'Source-update branch is stale or exceeds lock scope');
  const base = comparison.base_commit?.sha;
  if (!/^[0-9a-f]{40}$/.test(base || '')) throw new Error('Invalid base');
  const [beforeFile, afterFile] = await Promise.all([base,head].map(sha=>api(`repos/${TARGET}/contents/site/sources.lock.json?ref=${sha}`)));
  const decode = file => {
    if (file.encoding !== 'base64' || typeof file.content !== 'string' || file.content.length > 131072) throw new Error('Invalid lock');
    return JSON.parse(Buffer.from(file.content,'base64').toString());
  };
  const before = decode(beforeFile), after = decode(afterFile);
  const changes = lockRevisionChanges(before, after);
  if (!changes.length) return response(409, 'No source revisions changed');
  await Promise.all(changes.map(async ({repository,revision,previous})=>{
    const spec = registry.find(item=>item.repository===repository);
    if (!spec || repository===TARGET) throw new Error('Source not registered');
    const metadata = await api(`repos/${repository}`);
    if (metadata.private !== false || metadata.default_branch !== spec.branch) throw new Error('Source drift');
    const relation = await api(`repos/${repository}/compare/${revision}...${spec.branch}`);
    if (!['ahead','identical'].includes(relation.status)) throw new Error('Revision outside default branch');
    const forward = await api(`repos/${repository}/compare/${previous}...${revision}`);
    if (forward.status !== 'ahead') throw new Error('Source revision did not advance');
  }));
  const existing = await api(`repos/${TARGET}/pulls?state=open&head=${TARGET.split('/')[0]}:${branch}&base=main`);
  if (existing.length) return response(200, 'Source-update PR already exists');
  await api(`repos/${TARGET}/pulls`, 'POST', {title:'Refresh verified public-site sources',head:branch,base:'main',
    body:'The publishing App verified this signed Starter push: only registered source revisions change. Ordinary PR checks must pass before the publishing workflow can merge through normal branch rules. No review approval or rule bypass is performed.'});
  return response(201, 'Source-update PR created; ordinary PR checks must pass');
}

export function lockRevisionChanges(before, after) {
  const expected = structuredClone(before);
  const changes = [];
  for (const group of ['components','publications']) {
    for (const [key, item] of Object.entries(before[group] || {})) {
      const next = after[group]?.[key];
      if (!next) throw new Error('Lock structure changed');
      if (next.revision !== item.revision) {
        if (key === 'starter' || !/^[0-9a-f]{40}$/.test(next.revision || '')) throw new Error('Invalid source revision');
        expected[group][key].revision = next.revision;
        changes.push({repository:item.repository,revision:next.revision,previous:item.revision});
      }
    }
  }
  if (JSON.stringify(expected) !== JSON.stringify(after)) throw new Error('Lock scope changed');
  return changes;
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
      if (repository === TARGET) {
        if (payload.ref?.startsWith('refs/heads/automation/site-sources-')) {
          stage = 'source-update PR creation';
          return await openSourcePR(payload, env, registry, send);
        }
        return response(202, 'Starter push handled by Git integration');
      }
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
