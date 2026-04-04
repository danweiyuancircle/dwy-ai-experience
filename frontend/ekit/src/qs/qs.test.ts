describe('qs', () => {
  let stringify: typeof import('./index').stringify
  let parse: typeof import('./index').parse

  beforeAll(async () => {
    const mod = await import('./index')
    stringify = mod.stringify
    parse = mod.parse
  })

  describe('stringify', () => {
    it('应序列化基本对象', () => {
      const result = stringify({ name: 'alice', age: 25 })
      expect(result).toBe('name=alice&age=25')
    })

    it('应使用 repeat 格式序列化数组', () => {
      const result = stringify({ ids: [1, 2, 3] })
      expect(result).toBe('ids=1&ids=2&ids=3')
    })

    it('默认不添加 ? 前缀', () => {
      const result = stringify({ key: 'value' })
      expect(result).not.toMatch(/^\?/)
    })
  })

  describe('parse', () => {
    it('应解析基本查询字符串', () => {
      const result = parse('name=alice&age=25')
      expect(result).toEqual({ name: 'alice', age: '25' })
    })

    it('应自动忽略 ? 前缀', () => {
      const result = parse('?name=alice&age=25')
      expect(result).toEqual({ name: 'alice', age: '25' })
    })
  })

  describe('往返一致性', () => {
    it('stringify 后 parse 应还原原始对象（字符串值）', () => {
      const original = { name: 'bob', city: 'shanghai' }
      const str = stringify(original)
      const parsed = parse(str)
      expect(parsed).toEqual(original)
    })
  })

  describe('自定义 options', () => {
    it('stringify 应支持覆盖 addQueryPrefix', () => {
      const result = stringify({ key: 'value' }, { addQueryPrefix: true })
      expect(result).toBe('?key=value')
    })

    it('stringify 应支持覆盖 arrayFormat', () => {
      const result = stringify({ ids: [1, 2] }, { arrayFormat: 'comma' })
      expect(result).toBe('ids=1%2C2')
    })

    it('parse 应支持关闭 ignoreQueryPrefix', () => {
      const result = parse('?key=value', { ignoreQueryPrefix: false })
      expect(result).toHaveProperty('?key', 'value')
    })
  })
})
