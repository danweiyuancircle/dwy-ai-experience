import { describe, it, expect } from 'vitest'
import { isPhone, isEmail, isIdCard, isUrl, isRequired, minLength, maxLength } from './index'
import { phoneSchema, emailSchema, idCardSchema, urlSchema, requiredSchema, minLengthSchema, maxLengthSchema } from './schemas'

// ============================================================
// Original validator function tests (21 tests)
// ============================================================

describe('isPhone', () => {
  it('accepts valid Chinese mobile numbers', () => {
    expect(isPhone('13812345678')).toBe(true)
    expect(isPhone('19999999999')).toBe(true)
    expect(isPhone('15000000000')).toBe(true)
  })

  it('rejects numbers not starting with 1[3-9]', () => {
    expect(isPhone('12345678901')).toBe(false)
    expect(isPhone('10000000000')).toBe(false)
  })

  it('rejects wrong length', () => {
    expect(isPhone('1381234567')).toBe(false)
    expect(isPhone('138123456789')).toBe(false)
  })

  it('rejects non-numeric', () => {
    expect(isPhone('1381234567a')).toBe(false)
    expect(isPhone('')).toBe(false)
  })
})

describe('isEmail', () => {
  it('accepts valid emails', () => {
    expect(isEmail('user@example.com')).toBe(true)
    expect(isEmail('a.b@c.d')).toBe(true)
    expect(isEmail('test+tag@gmail.com')).toBe(true)
  })

  it('rejects invalid emails', () => {
    expect(isEmail('user@')).toBe(false)
    expect(isEmail('@example.com')).toBe(false)
    expect(isEmail('plainstring')).toBe(false)
    expect(isEmail('')).toBe(false)
    expect(isEmail('user @example.com')).toBe(false)
  })
})

describe('isIdCard', () => {
  it('accepts 18-digit ID cards', () => {
    expect(isIdCard('420681199901011234')).toBe(true)
    expect(isIdCard('11010119900101123X')).toBe(true)
    expect(isIdCard('11010119900101123x')).toBe(true)
  })

  it('rejects wrong length', () => {
    expect(isIdCard('42068119990101123')).toBe(false)
    expect(isIdCard('4206811999010112345')).toBe(false)
  })

  it('rejects non-numeric (except last X)', () => {
    expect(isIdCard('4206811999a1011234')).toBe(false)
    expect(isIdCard('')).toBe(false)
  })
})

describe('isUrl', () => {
  it('accepts valid URLs', () => {
    expect(isUrl('https://example.com')).toBe(true)
    expect(isUrl('http://localhost:3000')).toBe(true)
    expect(isUrl('ftp://files.example.com/doc.pdf')).toBe(true)
  })

  it('rejects invalid URLs', () => {
    expect(isUrl('not-a-url')).toBe(false)
    expect(isUrl('')).toBe(false)
    expect(isUrl('://missing-scheme')).toBe(false)
  })
})

describe('isRequired', () => {
  it('rejects null and undefined', () => {
    expect(isRequired(null)).toBe(false)
    expect(isRequired(undefined)).toBe(false)
  })

  it('rejects empty or whitespace-only strings', () => {
    expect(isRequired('')).toBe(false)
    expect(isRequired('   ')).toBe(false)
  })

  it('rejects empty arrays', () => {
    expect(isRequired([])).toBe(false)
  })

  it('accepts non-empty strings', () => {
    expect(isRequired('hello')).toBe(true)
    expect(isRequired(' a ')).toBe(true)
  })

  it('accepts non-empty arrays', () => {
    expect(isRequired([1])).toBe(true)
  })

  it('accepts numbers and booleans', () => {
    expect(isRequired(0)).toBe(true)
    expect(isRequired(false)).toBe(true)
  })
})

describe('minLength', () => {
  it('passes when string meets minimum', () => {
    expect(minLength('abc', 3)).toBe(true)
    expect(minLength('abcd', 3)).toBe(true)
  })

  it('fails when string is too short', () => {
    expect(minLength('ab', 3)).toBe(false)
    expect(minLength('', 1)).toBe(false)
  })
})

describe('maxLength', () => {
  it('passes when string is within maximum', () => {
    expect(maxLength('abc', 3)).toBe(true)
    expect(maxLength('ab', 3)).toBe(true)
  })

  it('fails when string exceeds maximum', () => {
    expect(maxLength('abcd', 3)).toBe(false)
  })
})

// ============================================================
// Schema tests
// ============================================================

describe('phoneSchema', () => {
  it('safeParse succeeds for valid phone', () => {
    const result = phoneSchema.safeParse('13812345678')
    expect(result.success).toBe(true)
  })

  it('safeParse fails with correct message for invalid phone', () => {
    const result = phoneSchema.safeParse('123')
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('请输入正确的手机号')
    }
  })
})

describe('emailSchema', () => {
  it('safeParse succeeds for valid email', () => {
    const result = emailSchema.safeParse('user@example.com')
    expect(result.success).toBe(true)
  })

  it('safeParse fails with correct message for invalid email', () => {
    const result = emailSchema.safeParse('not-email')
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('请输入正确的邮箱')
    }
  })
})

describe('idCardSchema', () => {
  it('safeParse succeeds for valid ID card', () => {
    const result = idCardSchema.safeParse('420681199901011234')
    expect(result.success).toBe(true)
  })

  it('safeParse fails with correct message for invalid ID card', () => {
    const result = idCardSchema.safeParse('123')
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('请输入正确的身份证号')
    }
  })
})

describe('urlSchema', () => {
  it('safeParse succeeds for valid URL', () => {
    const result = urlSchema.safeParse('https://example.com')
    expect(result.success).toBe(true)
  })

  it('safeParse succeeds for ftp URL', () => {
    const result = urlSchema.safeParse('ftp://files.example.com/doc.pdf')
    expect(result.success).toBe(true)
  })

  it('safeParse fails with correct message for invalid URL', () => {
    const result = urlSchema.safeParse('not-a-url')
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('请输入正确的 URL')
    }
  })
})

describe('requiredSchema', () => {
  it('safeParse succeeds for non-empty value', () => {
    expect(requiredSchema.safeParse('hello').success).toBe(true)
    expect(requiredSchema.safeParse(0).success).toBe(true)
    expect(requiredSchema.safeParse([1]).success).toBe(true)
  })

  it('safeParse fails with correct message for empty value', () => {
    const result = requiredSchema.safeParse(null)
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('此项为必填')
    }
  })

  it('safeParse fails for whitespace-only strings', () => {
    expect(requiredSchema.safeParse('   ').success).toBe(false)
  })

  it('safeParse fails for empty arrays', () => {
    expect(requiredSchema.safeParse([]).success).toBe(false)
  })
})

describe('minLengthSchema', () => {
  it('creates schema that succeeds when string meets minimum', () => {
    const schema = minLengthSchema(3)
    expect(schema.safeParse('abc').success).toBe(true)
    expect(schema.safeParse('abcd').success).toBe(true)
  })

  it('creates schema that fails when string is too short', () => {
    const schema = minLengthSchema(3)
    const result = schema.safeParse('ab')
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('最少 3 个字符')
    }
  })

  it('respects different min values', () => {
    expect(minLengthSchema(1).safeParse('').success).toBe(false)
    expect(minLengthSchema(5).safeParse('hello').success).toBe(true)
    expect(minLengthSchema(5).safeParse('hi').success).toBe(false)
  })
})

describe('maxLengthSchema', () => {
  it('creates schema that succeeds when string is within maximum', () => {
    const schema = maxLengthSchema(3)
    expect(schema.safeParse('abc').success).toBe(true)
    expect(schema.safeParse('ab').success).toBe(true)
  })

  it('creates schema that fails when string exceeds maximum', () => {
    const schema = maxLengthSchema(3)
    const result = schema.safeParse('abcd')
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('最多 3 个字符')
    }
  })

  it('respects different max values', () => {
    expect(maxLengthSchema(10).safeParse('short').success).toBe(true)
    expect(maxLengthSchema(2).safeParse('abc').success).toBe(false)
  })
})
