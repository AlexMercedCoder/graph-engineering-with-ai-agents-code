// Calls every handler in src/api/routes.js the way the router does, with a
// request object and a callback, and reports whether each one answers.
// The unit tests call service functions directly, so a change to a service's
// signature can pass them while the router can no longer reach it.
// Exits 1 if any route errors or never calls back.
import { routes } from '../src/api/routes.js';

const TIMEOUT_MS = 1500;
let broken = 0;

for (const route of routes) {
  const outcome = await new Promise((resolve) => {
    const timer = setTimeout(() => resolve({ ok: false, text: 'NO RESPONSE (callback never called)' }), TIMEOUT_MS);
    try {
      route.handler({ params: { id: '1' } }, (err, data) => {
        clearTimeout(timer);
        if (err) resolve({ ok: false, text: `error: ${err.message}` });
        else resolve({ ok: true, text: JSON.stringify(data).slice(0, 60) });
      });
    } catch (err) {
      clearTimeout(timer);
      resolve({ ok: false, text: `threw: ${err.message}` });
    }
  });
  if (!outcome.ok) broken += 1;
  console.log(`${outcome.ok ? 'ok  ' : 'FAIL'}  ${route.method} ${route.path} -> ${outcome.text}`);
}

console.log(broken ? `${broken} of ${routes.length} routes broken` : `all ${routes.length} routes respond`);
process.exit(broken ? 1 : 0);
