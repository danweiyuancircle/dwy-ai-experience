import { describe, it, expect, afterEach } from 'vitest'
import { useMessageBox } from '@/composables/useMessageBox'

describe('useMessageBox', () => {
  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('escapes HTML in title to prevent XSS', () => {
    const msgbox = useMessageBox()
    msgbox.alert('<img src=x onerror="alert(1)">', '<b>title</b>')

    const titleEl = document.querySelector('.font-semibold')
    expect(titleEl).not.toBeNull()
    // textContent should show raw HTML tags, not render them
    expect(titleEl!.textContent).toBe('<b>title</b>')
    // Should not create a <b> element inside the title
    expect(titleEl!.querySelector('b')).toBeNull()
  })

  it('escapes HTML in message to prevent XSS', () => {
    const msgbox = useMessageBox()
    msgbox.alert('<script>alert("xss")</script>')

    const msgEl = document.querySelector('.text-muted-foreground')
    expect(msgEl).not.toBeNull()
    // textContent should show the raw script tag
    expect(msgEl!.textContent).toBe('<script>alert("xss")</script>')
    // Should not create a script element
    expect(document.querySelector('script')).toBeNull()
  })

  it('renders safe default button text', () => {
    const msgbox = useMessageBox()
    msgbox.confirm('msg', 'title')

    const confirmBtn = document.querySelector('.eui-msgbox-confirm')
    expect(confirmBtn!.textContent).toBe('确定')

    const cancelBtn = document.querySelector('.eui-msgbox-cancel')
    expect(cancelBtn!.textContent).toBe('取消')
  })
})
