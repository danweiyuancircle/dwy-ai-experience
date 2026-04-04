import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import {
  createRequest,
  tokenPlugin,
  headerPlugin,
  unwrapPlugin,
  refreshTokenPlugin,
  type RequestPlugin,
} from './index'

// Mock axios — vi.hoisted runs before vi.mock hoisting
const { axiosFn } = vi.hoisted(() => {
  return { axiosFn: vi.fn() }
})

vi.mock('axios', () => {
  const interceptors = () => {
    const handlers: any[] = []
    return {
      use: (fulfilled: any, rejected: any) => handlers.push({ fulfilled, rejected }),
      handlers,
    }
  }

  const createMock = vi.fn(() => {
    const instance: any = vi.fn()
    instance.interceptors = {
      request: interceptors(),
      response: interceptors(),
    }
    return instance
  })

  return {
    default: Object.assign(axiosFn, {
      create: createMock,
    }),
  }
})

describe('createRequest', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates axios instance with default options', () => {
    createRequest()
    expect(axios.create).toHaveBeenCalledWith({
      baseURL: '/api',
      timeout: 30000,
    })
  })

  it('creates axios instance with custom options', () => {
    createRequest({ baseURL: '/v2', timeout: 5000 })
    expect(axios.create).toHaveBeenCalledWith({
      baseURL: '/v2',
      timeout: 5000,
    })
  })

  it('registers request and response interceptors', () => {
    const instance = createRequest()
    expect(instance.interceptors.request.handlers).toHaveLength(1)
    expect(instance.interceptors.response.handlers).toHaveLength(1)
  })
})

describe('tokenPlugin', () => {
  it('sets Authorization header when token exists', () => {
    const plugin = tokenPlugin({ getToken: () => 'my-token' })
    const config = { headers: {} } as any
    const result = plugin.onRequest!(config)
    expect((result as any).headers.Authorization).toBe('Bearer my-token')
  })

  it('does not set header when token is null', () => {
    const plugin = tokenPlugin({ getToken: () => null })
    const config = { headers: {} } as any
    plugin.onRequest!(config)
    expect((config as any).headers.Authorization).toBeUndefined()
  })
})

describe('headerPlugin', () => {
  it('sets custom header when value exists', () => {
    const plugin = headerPlugin({ name: 'X-Tenant', getValue: () => 'tenant-1' })
    const config = { headers: {} } as any
    plugin.onRequest!(config)
    expect(config.headers['X-Tenant']).toBe('tenant-1')
  })

  it('does not set header when value is null', () => {
    const plugin = headerPlugin({ name: 'X-Tenant', getValue: () => null })
    const config = { headers: {} } as any
    plugin.onRequest!(config)
    expect(config.headers['X-Tenant']).toBeUndefined()
  })
})

describe('unwrapPlugin', () => {
  const plugin = unwrapPlugin()

  it('returns unwrapped data when code is 200', async () => {
    const response = { data: { code: 200, data: { id: 1 }, message: 'ok' } } as any
    const result = await plugin.onResponse!(response)
    expect(result).toEqual({ code: 200, data: { id: 1 }, message: 'ok' })
  })

  it('rejects when code is not 200', async () => {
    const response = { data: { code: 400, message: '参数错误' } } as any
    await expect(plugin.onResponse!(response)).rejects.toThrow('参数错误')
  })

  it('rejects with default message when message is empty', async () => {
    const response = { data: { code: 500 } } as any
    await expect(plugin.onResponse!(response)).rejects.toThrow('Error')
  })

  it('passes through non-wrapped responses', async () => {
    const response = { data: 'plain text' } as any
    const result = await plugin.onResponse!(response)
    expect(result).toBe(response)
  })
})

describe('refreshTokenPlugin', () => {
  it('calls refreshFn on 401 and retries request', async () => {
    const refreshFn = vi.fn().mockResolvedValue('new-token')
    const onRefreshFail = vi.fn()

    const plugin = refreshTokenPlugin({
      getRefreshToken: () => 'refresh-123',
      refreshFn,
      onRefreshFail,
    })

    const error = {
      response: { status: 401 },
      config: { url: '/api/users', headers: {} },
    } as any

    // Mock axios callable to return resolved value on retry
    axiosFn.mockResolvedValueOnce({ data: 'retried' })

    const result = await plugin.onResponseError!(error)
    expect(refreshFn).toHaveBeenCalledWith('refresh-123')
    expect(error.config.headers.Authorization).toBe('Bearer new-token')
    expect(result).toEqual({ data: 'retried' })
  })

  it('calls onRefreshFail when no refresh token', async () => {
    const onRefreshFail = vi.fn()

    const plugin = refreshTokenPlugin({
      getRefreshToken: () => null,
      refreshFn: vi.fn(),
      onRefreshFail,
    })

    const error = {
      response: { status: 401 },
      config: { url: '/api/users', headers: {} },
      message: 'Unauthorized',
    } as any

    await expect(plugin.onResponseError!(error)).rejects.toThrow('Unauthorized')
    expect(onRefreshFail).toHaveBeenCalled()
  })

  it('skips refresh for login URL', async () => {
    const refreshFn = vi.fn()
    const onRefreshFail = vi.fn()

    const plugin = refreshTokenPlugin({
      getRefreshToken: () => 'token',
      refreshFn,
      onRefreshFail,
    })

    const error = {
      response: { status: 401, data: { message: '认证失败' } },
      config: { url: '/auth/login', headers: {} },
      message: 'Unauthorized',
    } as any

    await expect(plugin.onResponseError!(error)).rejects.toThrow('认证失败')
    expect(refreshFn).not.toHaveBeenCalled()
  })

  it('extracts error message from response data', async () => {
    const plugin = refreshTokenPlugin({
      getRefreshToken: () => null,
      refreshFn: vi.fn(),
      onRefreshFail: vi.fn(),
    })

    const error = {
      response: { status: 401, data: { detail: '令牌过期' } },
      config: { url: '/api/data', headers: {} },
      message: 'Unauthorized',
    } as any

    await expect(plugin.onResponseError!(error)).rejects.toThrow('令牌过期')
  })
})
