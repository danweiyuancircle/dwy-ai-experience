/**
 * request 模块测试
 * 重构后 createRequest 返回 ekit 自有的 HttpClient（不再暴露 AxiosInstance）
 * 插件契约为 HttpConfig / HttpResponse / HttpError（不再是 axios 类型）
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  createRequest,
  tokenPlugin,
  headerPlugin,
  unwrapPlugin,
  refreshTokenPlugin,
  SUCCESS_CODE,
  type ApiResponse,
  type HttpConfig,
  type HttpResponse,
  type HttpError,
} from '@/request'

describe('createRequest', () => {
  it('returns an HttpClient with request / get / post / put / delete / patch / head methods', () => {
    const client = createRequest()
    for (const m of ['request', 'get', 'post', 'put', 'delete', 'patch', 'head'] as const) {
      expect(typeof (client as any)[m]).toBe('function')
    }
  })

  it('does not expose axios-specific properties (interceptors / defaults / create)', () => {
    const client = createRequest() as any
    expect(client.interceptors).toBeUndefined()
    expect(client.defaults).toBeUndefined()
    expect(client.create).toBeUndefined()
  })

  it('accepts custom options without throwing', () => {
    expect(() =>
      createRequest({
        baseURL: '/v2',
        timeout: 5000,
        headers: { 'X-App': 'ekit' },
        plugins: [],
      }),
    ).not.toThrow()
  })
})

describe('tokenPlugin', () => {
  it('sets Authorization header when token exists', async () => {
    const plugin = tokenPlugin({ getToken: () => 'my-token' })
    const config: HttpConfig = { headers: {} }
    const result = await plugin.onRequest!(config)
    expect(result.headers?.Authorization).toBe('Bearer my-token')
  })

  it('does not set header when token is null', async () => {
    const plugin = tokenPlugin({ getToken: () => null })
    const config: HttpConfig = { headers: {} }
    const result = await plugin.onRequest!(config)
    expect(result.headers?.Authorization).toBeUndefined()
  })
})

describe('headerPlugin', () => {
  it('sets custom header when value exists', async () => {
    const plugin = headerPlugin({ name: 'X-Tenant', getValue: () => 'tenant-1' })
    const config: HttpConfig = { headers: {} }
    const result = await plugin.onRequest!(config)
    expect(result.headers?.['X-Tenant']).toBe('tenant-1')
  })

  it('does not set header when value is null', async () => {
    const plugin = headerPlugin({ name: 'X-Tenant', getValue: () => null })
    const config: HttpConfig = { headers: {} }
    const result = await plugin.onRequest!(config)
    expect(result.headers?.['X-Tenant']).toBeUndefined()
  })
})

describe('unwrapPlugin', () => {
  const plugin = unwrapPlugin()

  function makeResponse<T>(data: T): HttpResponse<T> {
    return { data, status: 200, statusText: 'OK', headers: {}, config: {} }
  }

  function makeApiResponse<T>(overrides: Partial<ApiResponse<T>>): ApiResponse<T> {
    return {
      code: SUCCESS_CODE,
      message: 'success',
      data: null,
      timestamp: 1713610245,
      ...overrides,
    } as ApiResponse<T>
  }

  it('replaces response.data with business payload when code is "SUCCESS"', async () => {
    const response = makeResponse(makeApiResponse({ data: { id: 1 } }))
    const result = await plugin.onResponse!(response)
    expect(result.data).toEqual({ id: 1 })
  })

  it('keeps PageData structure intact when code is "SUCCESS"', async () => {
    const response = makeResponse(
      makeApiResponse({ data: { items: [{ id: 1 }], total: 50, page: 2, page_size: 20 } }),
    )
    const result = await plugin.onResponse!(response)
    expect(result.data).toEqual({ items: [{ id: 1 }], total: 50, page: 2, page_size: 20 })
  })

  it('rejects when code is not "SUCCESS"', async () => {
    const response = makeResponse(makeApiResponse({ code: 'NOT_FOUND', message: '用户不存在' }))
    await expect(plugin.onResponse!(response)).rejects.toThrow('用户不存在')
  })

  it('rejects with HttpError carrying businessCode and apiResponse', async () => {
    const apiResp = makeApiResponse({
      code: 'VALIDATION_ERROR',
      message: '请求参数校验失败',
      data: { errors: [{ field: 'body.email', message: 'invalid email' }] },
    })
    const response = makeResponse(apiResp)
    try {
      await plugin.onResponse!(response)
      throw new Error('should have rejected')
    } catch (err) {
      const e = err as HttpError
      expect(e).toBeInstanceOf(Error)
      expect(e.message).toBe('请求参数校验失败')
      expect(e.businessCode).toBe('VALIDATION_ERROR')
      expect(e.apiResponse).toEqual(apiResp)
      expect(e.response).toBe(response)
    }
  })

  it('rejects with default message when message is empty', async () => {
    const response = makeResponse(makeApiResponse({ code: 'INTERNAL_ERROR', message: '' }))
    await expect(plugin.onResponse!(response)).rejects.toThrow('Error')
  })

  it('passes through non-wrapped responses', async () => {
    const response = makeResponse('plain text')
    const result = await plugin.onResponse!(response)
    expect(result).toBe(response)
  })

  it('passes through responses without code field', async () => {
    const response = makeResponse({ foo: 'bar' })
    const result = await plugin.onResponse!(response)
    expect(result).toBe(response)
  })
})

describe('refreshTokenPlugin', () => {
  function makeError(overrides: Partial<HttpError> & { config?: HttpConfig; response?: Partial<HttpResponse> } = {}): HttpError {
    const err = new Error(overrides.message ?? 'Request failed') as HttpError
    err.config = overrides.config
    err.response = overrides.response
      ? {
          data: undefined,
          status: 401,
          statusText: '',
          headers: {},
          config: {},
          ...overrides.response,
        }
      : undefined
    return err
  }

  it('calls refreshFn on 401 and retries request via retry callback', async () => {
    const refreshFn = vi.fn().mockResolvedValue('new-token')
    const retry = vi.fn().mockResolvedValue({ data: 'retried', status: 200, statusText: 'OK', headers: {}, config: {} })
    const onRefreshFail = vi.fn()

    const plugin = refreshTokenPlugin({
      getRefreshToken: () => 'refresh-123',
      refreshFn,
      onRefreshFail,
      retry,
    })

    const error = makeError({
      response: { status: 401 },
      config: { url: '/api/users', headers: {} },
    })

    const result = await plugin.onResponseError!(error)
    expect(refreshFn).toHaveBeenCalledWith('refresh-123')
    expect(retry).toHaveBeenCalledWith(
      expect.objectContaining({
        url: '/api/users',
        headers: expect.objectContaining({ Authorization: 'Bearer new-token' }),
      }),
    )
    expect(result).toEqual(expect.objectContaining({ data: 'retried' }))
    expect(onRefreshFail).not.toHaveBeenCalled()
  })

  it('calls onRefreshFail when no refresh token', async () => {
    const onRefreshFail = vi.fn()
    const plugin = refreshTokenPlugin({
      getRefreshToken: () => null,
      refreshFn: vi.fn(),
      onRefreshFail,
      retry: vi.fn(),
    })

    const error = makeError({
      response: { status: 401 },
      config: { url: '/api/users', headers: {} },
      message: 'Unauthorized',
    })

    await expect(plugin.onResponseError!(error)).rejects.toThrow('Unauthorized')
    expect(onRefreshFail).toHaveBeenCalled()
  })

  it('skips refresh for login URL', async () => {
    const refreshFn = vi.fn()
    const retry = vi.fn()
    const plugin = refreshTokenPlugin({
      getRefreshToken: () => 'token',
      refreshFn,
      onRefreshFail: vi.fn(),
      retry,
    })

    const error = makeError({
      response: { status: 401, data: { message: '认证失败' } as any },
      config: { url: '/auth/login', headers: {} },
      message: 'Unauthorized',
    })

    await expect(plugin.onResponseError!(error)).rejects.toThrow('认证失败')
    expect(refreshFn).not.toHaveBeenCalled()
    expect(retry).not.toHaveBeenCalled()
  })

  it('prefers ApiResponse message over FastAPI detail field', async () => {
    const plugin = refreshTokenPlugin({
      getRefreshToken: () => null,
      refreshFn: vi.fn(),
      onRefreshFail: vi.fn(),
      retry: vi.fn(),
    })

    const error = makeError({
      response: {
        status: 401,
        data: {
          code: 'AUTHENTICATION_FAILED',
          message: '认证失败',
          data: null,
          timestamp: 1713610245,
          // 额外的 detail 字段，message 优先
          detail: 'legacy detail',
        } as any,
      },
      config: { url: '/api/data', headers: {} },
      message: 'Unauthorized',
    })

    await expect(plugin.onResponseError!(error)).rejects.toThrow('认证失败')
  })

  it('falls back to FastAPI detail field when ApiResponse message missing', async () => {
    const plugin = refreshTokenPlugin({
      getRefreshToken: () => null,
      refreshFn: vi.fn(),
      onRefreshFail: vi.fn(),
      retry: vi.fn(),
    })

    const error = makeError({
      response: { status: 401, data: { detail: '令牌过期' } as any },
      config: { url: '/api/data', headers: {} },
      message: 'Unauthorized',
    })

    await expect(plugin.onResponseError!(error)).rejects.toThrow('令牌过期')
  })

  it('attaches businessCode and apiResponse to rejected error when body is ApiResponse', async () => {
    const plugin = refreshTokenPlugin({
      getRefreshToken: () => null,
      refreshFn: vi.fn(),
      onRefreshFail: vi.fn(),
      retry: vi.fn(),
    })

    const apiResp = {
      code: 'AUTHENTICATION_FAILED',
      message: '认证失败',
      data: null,
      timestamp: 1713610245,
    }
    const error = makeError({
      response: { status: 401, data: apiResp as any },
      config: { url: '/api/data', headers: {} },
      message: 'Unauthorized',
    })

    try {
      await plugin.onResponseError!(error)
      throw new Error('should have rejected')
    } catch (err) {
      const e = err as HttpError
      expect(e.message).toBe('认证失败')
      expect(e.businessCode).toBe('AUTHENTICATION_FAILED')
      expect(e.apiResponse).toEqual(apiResp)
    }
  })

  it('calls onRefreshFail when refreshFn throws', async () => {
    const onRefreshFail = vi.fn()
    const retry = vi.fn()
    const plugin = refreshTokenPlugin({
      getRefreshToken: () => 'refresh-123',
      refreshFn: vi.fn().mockRejectedValue(new Error('refresh failed')),
      onRefreshFail,
      retry,
    })

    const error = makeError({
      response: { status: 401 },
      config: { url: '/api/users', headers: {} },
      message: 'Unauthorized',
    })

    await expect(plugin.onResponseError!(error)).rejects.toThrow('Unauthorized')
    expect(onRefreshFail).toHaveBeenCalled()
    expect(retry).not.toHaveBeenCalled()
  })
})

