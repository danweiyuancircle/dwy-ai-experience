import { describe, it, expect, afterEach } from 'vitest'
import { useNotification } from '@/composables/useNotification'

describe('useNotification', () => {
  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('renders notification with title', () => {
    const notification = useNotification()
    notification.info({ title: 'Test Title' })

    const el = document.querySelector('.font-medium')
    expect(el).not.toBeNull()
    expect(el!.textContent).toBe('Test Title')
  })

  it('escapes HTML in title to prevent XSS', () => {
    const notification = useNotification()
    notification.info({ title: '<img src=x onerror="alert(1)">' })

    const el = document.querySelector('.font-medium')
    expect(el).not.toBeNull()
    // textContent should show the raw text, not execute HTML
    expect(el!.textContent).toBe('<img src=x onerror="alert(1)">')
    // Should not create an actual img element
    expect(document.querySelector('img')).toBeNull()
  })

  it('escapes HTML in message to prevent XSS', () => {
    const notification = useNotification()
    notification.info({ title: 'safe', message: '<script>alert("xss")</script>' })

    const msgEl = document.querySelector('.text-muted-foreground.mt-1')
    expect(msgEl).not.toBeNull()
    // textContent should show the raw script tag text
    expect(msgEl!.textContent).toBe('<script>alert("xss")</script>')
    // Should not create a script element
    expect(document.querySelector('script')).toBeNull()
  })

  it('does not double-escape already safe text', () => {
    const notification = useNotification()
    notification.info({ title: 'Hello & World' })

    const el = document.querySelector('.font-medium')
    expect(el!.textContent).toBe('Hello & World')
  })
})
