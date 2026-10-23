/** 只从安装的 tgz 公开入口消费，不允许源码 alias 掩盖导出或 Vue 实例问题。 */
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createSSRApp, effectScope, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { EConfigProvider } from '@dwydev/eui'
import { AdminShell, createAdminShell } from '@dwydev/admin-kit'
import { PagedTable, RequestFeedback, RecordCode } from '@dwydev/admin-kit/components'
import { usePagedList } from '@dwydev/admin-kit/composables'
import { usePagedList as compatibleList } from '@dwydev/admin-kit/paged-list'
import { STATUS_TONE } from '@dwydev/admin-kit/status/tone'

assert.equal(typeof AdminShell, 'object')
assert.equal(createAdminShell({ title: 'Consumer', modules: [] }).shellProps.title, 'Consumer')
assert.equal(compatibleList, usePagedList)
assert.ok(STATUS_TONE)
assert.ok(readFileSync(new URL(import.meta.resolve('@dwydev/admin-kit/style.css')), 'utf8').length > 0)
const scope = effectScope()
let finish
const list = scope.run(() => usePagedList({
  fetcher: () => new Promise(resolve => { finish = resolve }),
}))
const pending = list.load()
scope.stop()
finish({ items: ['late'], total: 1 })
await pending
assert.deepEqual(list.items.value, [])
assert.equal(list.loading.value, false)
assert.equal(list.error.value, null)
assert.equal(typeof list.reset, 'function')
assert.equal(typeof list.invalidate, 'function')

const html = await renderToString(createSSRApp({
  render: () => h(EConfigProvider, () => [
    h(PagedTable, { columns: [{ key: 'name', title: 'Name' }], data: [{ name: 'Consumer row' }], rowKey: 'name' }),
    h(RequestFeedback, { error: 'unavailable' }),
    h(RecordCode, { text: 'artifact-record' }),
  ]),
}))
assert.ok(html.includes('Consumer row'))
assert.ok(html.includes('artifact-record'))
console.log('fresh admin-kit tgz: root/subpaths + lifecycle + real EUI SSR passed')
