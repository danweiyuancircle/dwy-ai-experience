import { describe, it, expect, beforeEach, vi } from 'vitest'
import { storage } from '@/storage'

describe('storage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  describe('set + get', () => {
    it('stores and retrieves string values', () => {
      storage.set('name', 'Alice')
      expect(storage.get('name')).toBe('Alice')
    })

    it('stores and retrieves objects', () => {
      const user = { id: 1, name: 'Alice' }
      storage.set('user', user)
      expect(storage.get('user')).toEqual(user)
    })

    it('stores and retrieves arrays', () => {
      storage.set('tags', [1, 2, 3])
      expect(storage.get('tags')).toEqual([1, 2, 3])
    })

    it('stores and retrieves numbers', () => {
      storage.set('count', 42)
      expect(storage.get('count')).toBe(42)
    })

    it('stores and retrieves booleans', () => {
      storage.set('active', true)
      expect(storage.get('active')).toBe(true)
    })

    it('stores null as JSON', () => {
      storage.set('empty', null)
      expect(storage.get('empty')).toBeNull()
    })
  })

  describe('get with defaults', () => {
    it('returns default when key does not exist', () => {
      expect(storage.get('missing', 'fallback')).toBe('fallback')
    })

    it('returns undefined when key does not exist and no default', () => {
      expect(storage.get('missing')).toBeUndefined()
    })

    it('returns stored value even when default is provided', () => {
      storage.set('key', 'stored')
      expect(storage.get('key', 'default')).toBe('stored')
    })
  })

  describe('get with non-JSON values', () => {
    it('returns raw value when JSON parse fails', () => {
      localStorage.setItem('raw', 'not-json')
      expect(storage.get('raw')).toBe('not-json')
    })
  })

  describe('remove', () => {
    it('removes a stored key', () => {
      storage.set('key', 'value')
      storage.remove('key')
      expect(storage.get('key')).toBeUndefined()
    })
  })

  describe('clear', () => {
    it('removes all keys', () => {
      storage.set('a', 1)
      storage.set('b', 2)
      storage.clear()
      expect(storage.get('a')).toBeUndefined()
      expect(storage.get('b')).toBeUndefined()
    })
  })
})
