import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'
import EAlertDialog from '@/components/alert-dialog/EAlertDialog.vue'
import EConfirmDialog from '@/components/confirm-dialog/EConfirmDialog.vue'
import EDialog from '@/components/dialog/EDialog.vue'
import { useMessageBox } from '@/composables/useMessageBox'

/**
 * 断言遮罩表面与 EDialog 2.1.0 起的标准一致。
 * 不读共享常量：常量写错时这里仍要失败。
 */
function expectDialogOverlaySurface(overlay: Element | null) {
  expect(overlay).not.toBeNull()
  const className = overlay!.className
  expect(className).toContain('bg-black/30')
  expect(className).toContain('backdrop-blur-sm')
  expect(className).not.toContain('bg-black/80')
}

function findOverlay(): Element | null {
  return [...document.querySelectorAll('div')].find((el) => {
    const className = el.className
    return className.includes('fixed') && className.includes('inset-0') && className.includes('bg-black/')
  }) ?? null
}

describe('弹框遮罩表面', () => {
  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('EDialog 遮罩是 30% 黑加背景模糊', async () => {
    const wrapper = mount(EDialog, {
      attachTo: document.body,
      props: { open: true, title: '修改邮箱' },
    })
    await flushPromises()
    expectDialogOverlaySurface(document.querySelector('[data-slot="dialog-overlay"]'))
    wrapper.unmount()
  })

  it('EAlertDialog 遮罩与 EDialog 相同', async () => {
    const wrapper = mount(EAlertDialog, {
      attachTo: document.body,
      props: { open: true, title: '确认', description: '此操作不可撤销。' },
    })
    await flushPromises()
    expectDialogOverlaySurface(document.querySelector('[data-slot="alert-dialog-overlay"]'))
    wrapper.unmount()
  })

  it('EConfirmDialog 遮罩与 EDialog 相同', async () => {
    const wrapper = mount(EConfirmDialog, {
      attachTo: document.body,
      props: { open: true, title: '删除公告', message: '删除后不可恢复。' },
    })
    await flushPromises()
    expectDialogOverlaySurface(findOverlay())
    wrapper.unmount()
  })

  it('useMessageBox 遮罩与 EDialog 相同', () => {
    useMessageBox().confirm('删除「服务全面升级通知」？删除后不可恢复。', '删除公告')
    expectDialogOverlaySurface(findOverlay())
  })
})
