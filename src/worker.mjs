import manifest from '../site/publications.json';
import { makeHandler } from './github-app.mjs';
const handle = makeHandler([...Object.values(manifest.components), ...Object.values(manifest.publications || {})]);
export default {
  async fetch(request, env) {
    if (new URL(request.url).pathname.startsWith('/_events/')) return handle(request, env);
    return env.ASSETS.fetch(request);
  },
};
