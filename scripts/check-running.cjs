const assert = require('node:assert/strict');
const base = process.env.APP_URL || 'http://127.0.0.1:8080';

async function checkRole(username, origin) {
  const jar = {};
  async function request(path, method = 'GET', body) {
    const response = await fetch(base + '/api/v1/' + path, {
      method,
      headers: {
        Origin: origin,
        Cookie: Object.entries(jar).map(([key, value]) => `${key}=${value}`).join('; '),
        'Content-Type': 'application/json',
        'X-CSRFToken': jar.csrftoken || '',
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    for (const cookie of response.headers.getSetCookie()) {
      const [key, value] = cookie.split(';')[0].split('=');
      jar[key] = value;
    }
    const text = await response.text();
    assert.equal(response.status, 200, `${method} ${path}: ${text.slice(0, 180)}`);
    return JSON.parse(text);
  }
  await request('auth/csrf/');
  await request('auth/login/', 'POST', { username, password: process.env.DEMO_PASSWORD || 'Demo-Credit-2026!' });
  const profile = await request('auth/me/');
  assert.equal(profile.username, username);
  assert.equal(profile.is_staff, username === 'bank');
  const applications = await request('applications/');
  const products = await request('products/');
  assert.ok(products.count >= 3);
  await request('auth/logout/', 'POST');
  console.log(`${origin}: ${username} login/profile/catalog/applications/logout OK (${applications.count} applications)`);
}

(async () => {
  const page = await fetch(base + '/');
  assert.equal(page.status, 200);
  assert.match(await page.text(), /<div id="root">/);
  for (const path of ['/health/', '/api/docs/', '/api/schema/']) {
    const response = await fetch(base + path);
    assert.equal(response.status, 200, path);
    if (path === '/health/') assert.equal((await response.json()).status, 'ok');
    console.log(`${path}: HTTP 200`);
  }
  for (const origin of new Set([new URL(base).origin, ...((process.env.TEST_ORIGINS || '').split(',').filter(Boolean))])) {
    await checkRole('demo_a', origin);
    await checkRole('bank', origin);
  }
  console.log('Running application checks passed with browser Origin headers.');
})().catch(error => { console.error(error.message); process.exitCode = 1; });
