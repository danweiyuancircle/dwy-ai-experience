/**
 * AdminShell 窄屏顶栏命中：中间空槽不接收指针,避免叠到汉堡上。
 * 只断言源码 class(读 ?raw),不挂载整棵壳(会拉 ekit/dayjs 全链)。
 */
import { describe, expect, it } from 'vitest'
import source from '../../src/components/AdminShell.vue?raw'

describe('AdminShell 窄屏顶栏命中', () => {
  it('中间槽本身不接收指针，避免空槽叠到汉堡上', () => {
    expect(source).toContain('data-slot="admin-header-center"')
    expect(source).toContain('data-slot="admin-header-extra"')
    const centerBlock = source.slice(
      source.indexOf('data-slot="admin-header-center"'),
      source.indexOf('data-slot="admin-header-extra"'),
    )
    expect(centerBlock).not.toContain('pointer-events-auto')
    expect(source).toContain('data-slot="admin-header-extra"')
    const extraBlock = source.slice(source.indexOf('data-slot="admin-header-extra"'))
    expect(extraBlock).toContain('pointer-events-auto')
  })
})
