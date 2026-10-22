import assert from 'node:assert/strict'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { EConfigProvider } from '@dwydev/eui'
import { AdminLogin, createAdminAuthApi, createAdminSession } from '@dwydev/auth-web'

globalThis.location = new URL('https://console.example.invalid/admin/')
const requests = []
globalThis.fetch = async (url, options) => {
  requests.push({ url, options })
  return new Response(JSON.stringify({ code: 'SUCCESS', data: url.endsWith('/logout') ? null : { username: 'operator' } }))
}
const api = createAdminAuthApi({ baseURL: '/api/admin' })
const session = createAdminSession(api)
await session.login('operator', 'smoke-only-password')
assert.equal(session.administrator.value.username, 'operator')
assert.equal(requests[0].options.credentials, 'same-origin')
assert.equal(requests[0].options.redirect, 'error')
await session.logout()
assert.equal(session.administrator.value, null)
const html = await renderToString(createSSRApp({
  render: () => h(EConfigProvider, () => h(AdminLogin, { auth: api, brand: 'Smoke Console', homePath: '/', loginPath: '/login' })),
}))
assert.ok(html.includes('Smoke Console'))
assert.ok(html.includes('autocomplete="current-password"'))
console.log('fresh tgz consumer: API + memory session + Vue component SSR passed')
