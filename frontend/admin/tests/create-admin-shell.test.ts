/**
 * @dwydev/admin 装配逻辑单测
 */
import { describe, expect, it } from 'vitest'
import {
  collectMenuItems,
  createAdminShell,
  normalizeRoutePath,
  resolveFeatures,
} from '../src/create-admin-shell'
import { defineAdminModule } from '../src/define-admin-module'

describe('normalizeRoutePath', () => {
  it('相对 path 补前导斜杠', () => {
    expect(normalizeRoutePath('quota')).toBe('/quota')
  })

  it('已是绝对 path 时不重复前缀', () => {
    expect(normalizeRoutePath('/keys')).toBe('/keys')
  })

  it('根 path 保持为 /', () => {
    expect(normalizeRoutePath('/')).toBe('/')
    expect(normalizeRoutePath('')).toBe('/')
  })
})

describe('resolveFeatures', () => {
  it('默认全部 chrome 开启，command 关闭', () => {
    expect(resolveFeatures()).toEqual({
      theme: true,
      notifications: true,
      userMenu: true,
      command: false,
    })
  })

  it('可显式关闭 theme', () => {
    expect(resolveFeatures({ theme: false }).theme).toBe(false)
  })
})

describe('createAdminShell', () => {
  it('按 order 合并菜单并注入默认 meta', () => {
    const shell = createAdminShell({
      title: 'Test',
      logo: '/logo.png',
      logoTo: '/dashboard',
      routeMetaDefaults: { requiresAuth: true, layout: 'admin' },
      modules: [
        defineAdminModule({
          id: 'b',
          order: 20,
          menu: { key: '/b', label: 'B' },
          routes: [{ path: 'b', name: 'b', component: { template: '<div />' }, meta: { title: 'B' } }],
        }),
        defineAdminModule({
          id: 'a',
          order: 10,
          menu: {
            key: 'group-a',
            label: 'A 组',
            children: [{ key: '/a', label: 'A' }],
          },
          routes: [{ path: '/a', name: 'a', component: { template: '<div />' }, meta: { title: 'A' } }],
        }),
      ],
    })

    expect(shell.menuItems.map((m) => m.key)).toEqual(['group-a', '/b'])
    expect(shell.menuItems[0].children?.[0].key).toBe('/a')
    expect(shell.routes.map((r) => r.path)).toEqual(['/a', '/b'])
    expect(shell.routes[0].meta).toMatchObject({
      title: 'A',
      requiresAuth: true,
      layout: 'admin',
    })
    expect(shell.shellProps.title).toBe('Test')
    expect(shell.shellProps.logoTo).toBe('/dashboard')
    expect(shell.shellProps.features?.userMenu).toBe(true)
  })

  it('showInMenu=false 时只注册路由不出现在菜单', () => {
    const modules = [
      defineAdminModule({
        id: 'hidden',
        showInMenu: false,
        menu: { key: '/hidden', label: '隐藏' },
        routes: [{ path: '/hidden', name: 'hidden', component: { template: '<div />' } }],
      }),
      defineAdminModule({
        id: 'visible',
        menu: { key: '/v', label: '可见' },
        routes: [{ path: '/v', name: 'v', component: { template: '<div />' } }],
      }),
    ]
    expect(collectMenuItems(modules).map((m) => m.key)).toEqual(['/v'])
  })
})
