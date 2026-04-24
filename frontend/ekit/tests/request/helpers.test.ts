/**
 * dwyeapi 响应辅助工具测试:extractValidationErrors / isApiBusinessError
 */
import { describe, it, expect } from 'vitest'
import {
  extractValidationErrors,
  isApiBusinessError,
  SUCCESS_CODE,
  type ApiResponse,
  type HttpError,
  type ValidationErrorData,
} from '@/request'

function makeApiResponse<T>(overrides: Partial<ApiResponse<T>>): ApiResponse<T> {
  return {
    code: SUCCESS_CODE,
    message: 'success',
    data: null,
    timestamp: 1713610245,
    ...overrides,
  } as ApiResponse<T>
}

function makeBusinessError<T>(code: string, data: T | null, message = 'error'): HttpError {
  const err = new Error(message) as HttpError
  err.businessCode = code
  err.apiResponse = makeApiResponse({ code, message, data }) as ApiResponse<unknown>
  return err
}

describe('isApiBusinessError', () => {
  it('returns true for errors with businessCode and apiResponse', () => {
    const err = makeBusinessError('NOT_FOUND', null, '用户不存在')
    expect(isApiBusinessError(err)).toBe(true)
  })

  it('returns false for plain Error without businessCode', () => {
    expect(isApiBusinessError(new Error('network'))).toBe(false)
  })

  it('returns false for non-Error values', () => {
    expect(isApiBusinessError(null)).toBe(false)
    expect(isApiBusinessError(undefined)).toBe(false)
    expect(isApiBusinessError('string')).toBe(false)
    expect(isApiBusinessError({ businessCode: 'X', apiResponse: {} })).toBe(false)
  })
})

describe('extractValidationErrors', () => {
  it('converts errors array to flat record from HttpError input', () => {
    const err = makeBusinessError<ValidationErrorData>(
      'VALIDATION_ERROR',
      {
        errors: [
          { field: 'body.email', message: 'invalid email' },
          { field: 'body.age', message: 'must be >= 0' },
          { field: 'query.page_size', message: 'must be <= 100' },
        ],
      },
      '请求参数校验失败',
    )
    expect(extractValidationErrors(err)).toEqual({
      email: 'invalid email',
      age: 'must be >= 0',
      page_size: 'must be <= 100',
    })
  })

  it('strips body. / query. / path. / header. / cookie. prefixes', () => {
    const err = makeBusinessError<ValidationErrorData>(
      'VALIDATION_ERROR',
      {
        errors: [
          { field: 'body.title', message: 'b' },
          { field: 'query.q', message: 'q' },
          { field: 'path.id', message: 'p' },
          { field: 'header.X-Auth', message: 'h' },
          { field: 'cookie.session', message: 'c' },
          { field: 'no_prefix', message: 'n' },
        ],
      },
    )
    expect(extractValidationErrors(err)).toEqual({
      title: 'b',
      q: 'q',
      id: 'p',
      'X-Auth': 'h',
      session: 'c',
      no_prefix: 'n',
    })
  })

  it('keeps nested dot paths intact (body.items.0.name → items.0.name)', () => {
    const err = makeBusinessError<ValidationErrorData>(
      'VALIDATION_ERROR',
      {
        errors: [{ field: 'body.items.0.name', message: 'required' }],
      },
    )
    expect(extractValidationErrors(err)).toEqual({
      'items.0.name': 'required',
    })
  })

  it('later entries override earlier ones for the same field', () => {
    const err = makeBusinessError<ValidationErrorData>(
      'VALIDATION_ERROR',
      {
        errors: [
          { field: 'body.email', message: 'first' },
          { field: 'body.email', message: 'second' },
        ],
      },
    )
    expect(extractValidationErrors(err)).toEqual({ email: 'second' })
  })

  it('accepts a full ApiResponse envelope as input', () => {
    const resp = makeApiResponse<ValidationErrorData>({
      code: 'VALIDATION_ERROR',
      message: '校验失败',
      data: { errors: [{ field: 'body.name', message: 'too short' }] },
    })
    expect(extractValidationErrors(resp)).toEqual({ name: 'too short' })
  })

  it('accepts a bare ValidationErrorData as input', () => {
    const raw: ValidationErrorData = {
      errors: [{ field: 'body.foo', message: 'bar' }],
    }
    expect(extractValidationErrors(raw)).toEqual({ foo: 'bar' })
  })

  it('returns empty object for non-validation inputs', () => {
    expect(extractValidationErrors(null)).toEqual({})
    expect(extractValidationErrors(undefined)).toEqual({})
    expect(extractValidationErrors(new Error('plain'))).toEqual({})
    expect(extractValidationErrors(makeBusinessError('NOT_FOUND', null))).toEqual({})
  })

  it('handles empty errors array', () => {
    const err = makeBusinessError<ValidationErrorData>('VALIDATION_ERROR', { errors: [] })
    expect(extractValidationErrors(err)).toEqual({})
  })
})
