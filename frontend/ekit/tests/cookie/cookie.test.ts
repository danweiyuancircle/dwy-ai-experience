import { describe, it, expect, beforeEach, vi } from 'vitest'
import { nextTick } from 'vue'
import Cookies from 'js-cookie'
import { cookie, useCookie } from '@/cookie'

describe('cookie', () => {
  beforeEach(() => {
    // Clear all cookies before each test
    document.cookie.split(';').forEach((c) => {
      const name = c.trim().split('=')[0]
      if (name) Cookies.remove(name)
    })
  })

  describe('set + get', () => {
    it('stores and retrieves string values', () => {
      cookie.set('name', 'Alice')
      expect(cookie.get('name')).toBe('Alice')
    })

    it('stores and retrieves objects (JSON serialization)', () => {
      const user = { id: 1, name: 'Alice' }
      cookie.set('user', user)
      expect(cookie.get('user')).toEqual(user)
    })

    it('stores and retrieves arrays', () => {
      cookie.set('tags', [1, 2, 3])
      expect(cookie.get('tags')).toEqual([1, 2, 3])
    })

    it('stores and retrieves numbers', () => {
      cookie.set('count', 42)
      expect(cookie.get('count')).toBe(42)
    })

    it('stores and retrieves booleans', () => {
      cookie.set('active', true)
      expect(cookie.get('active')).toBe(true)
    })

    it('returns undefined for non-existent key', () => {
      expect(cookie.get('missing')).toBeUndefined()
    })
  })

  describe('remove', () => {
    it('removes a stored key', () => {
      cookie.set('key', 'value')
      cookie.remove('key')
      expect(cookie.get('key')).toBeUndefined()
    })
  })

  describe('useCookie', () => {
    it('creates a ref with current cookie value', () => {
      cookie.set('token', 'abc123')
      const token = useCookie('token')
      expect(token.value).toBe('abc123')
    })

    it('uses default value when cookie does not exist', () => {
      const theme = useCookie('theme', 'light')
      expect(theme.value).toBe('light')
    })

    it('syncs ref changes to cookie', async () => {
      const lang = useCookie('lang', 'zh')
      lang.value = 'en'
      await nextTick()
      expect(cookie.get('lang')).toBe('en')
    })

    it('removes cookie when ref is set to undefined', async () => {
      cookie.set('temp', 'data')
      const temp = useCookie('temp')
      expect(temp.value).toBe('data')

      temp.value = undefined
      await nextTick()
      expect(cookie.get('temp')).toBeUndefined()
    })

    it('removes cookie when ref is set to null', async () => {
      cookie.set('temp', 'data')
      const temp = useCookie<string | null>('temp')
      expect(temp.value).toBe('data')

      temp.value = null
      await nextTick()
      expect(cookie.get('temp')).toBeUndefined()
    })

    it('syncs object changes to cookie', async () => {
      const settings = useCookie<{ dark: boolean }>('settings', { dark: false })
      settings.value = { dark: true }
      await nextTick()
      expect(cookie.get<{ dark: boolean }>('settings')).toEqual({ dark: true })
    })
  })
})
