import { describe, it, expect, vi, beforeEach } from 'vitest'
import { formatFileSize, saveBlob, downloadFile } from '@/file'

vi.mock('file-saver', () => ({
  saveAs: vi.fn(),
}))

import { saveAs } from 'file-saver'

describe('formatFileSize', () => {
  it('should return "0 B" for 0 bytes', () => {
    expect(formatFileSize(0)).toBe('0 B')
  })

  it('should format bytes correctly', () => {
    expect(formatFileSize(1023)).toBe('1023 B')
  })

  it('should format KB correctly', () => {
    expect(formatFileSize(1024)).toBe('1 KB')
  })

  it('should format MB correctly', () => {
    expect(formatFileSize(1048576)).toBe('1 MB')
  })

  it('should format GB correctly', () => {
    expect(formatFileSize(1073741824)).toBe('1 GB')
  })

  it('should format TB correctly', () => {
    expect(formatFileSize(1099511627776)).toBe('1 TB')
  })

  it('should respect decimals parameter', () => {
    expect(formatFileSize(1536, 0)).toBe('2 KB')
    expect(formatFileSize(1536, 1)).toBe('1.5 KB')
    expect(formatFileSize(1536, 3)).toBe('1.5 KB')
  })

  it('should handle fractional sizes', () => {
    expect(formatFileSize(1500)).toBe('1.46 KB')
    expect(formatFileSize(1500000)).toBe('1.43 MB')
  })
})

describe('saveBlob', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should call saveAs with blob and filename', () => {
    const blob = new Blob(['test content'])
    saveBlob(blob, 'test.txt')
    expect(saveAs).toHaveBeenCalledWith(blob, 'test.txt')
  })
})

describe('downloadFile', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should make GET request by default and call saveAs', async () => {
    const mockResponse = {
      data: new Blob(['file content']),
      headers: {},
    }
    const mockRequest = vi.fn().mockResolvedValue(mockResponse)
    const mockInstance = { request: mockRequest } as any

    await downloadFile('/api/file', { requestInstance: mockInstance, filename: 'test.pdf' })

    expect(mockRequest).toHaveBeenCalledWith({
      url: '/api/file',
      method: 'GET',
      data: undefined,
      headers: undefined,
      responseType: 'blob',
    })
    expect(saveAs).toHaveBeenCalledWith(expect.any(Blob), 'test.pdf')
  })

  it('should support POST method with data', async () => {
    const mockResponse = {
      data: new Blob(['file content']),
      headers: {},
    }
    const mockRequest = vi.fn().mockResolvedValue(mockResponse)
    const mockInstance = { request: mockRequest } as any

    await downloadFile('/api/export', {
      requestInstance: mockInstance,
      method: 'POST',
      data: { ids: [1, 2, 3] },
      filename: 'export.xlsx',
    })

    expect(mockRequest).toHaveBeenCalledWith({
      url: '/api/export',
      method: 'POST',
      data: { ids: [1, 2, 3] },
      headers: undefined,
      responseType: 'blob',
    })
  })

  it('should extract filename from Content-Disposition header', async () => {
    const mockResponse = {
      data: new Blob(['file content']),
      headers: {
        'content-disposition': 'attachment; filename="report.pdf"',
      },
    }
    const mockRequest = vi.fn().mockResolvedValue(mockResponse)
    const mockInstance = { request: mockRequest } as any

    await downloadFile('/api/file', { requestInstance: mockInstance })

    expect(saveAs).toHaveBeenCalledWith(expect.any(Blob), 'report.pdf')
  })

  it('should extract filename from Content-Disposition with UTF-8 encoding', async () => {
    const mockResponse = {
      data: new Blob(['file content']),
      headers: {
        'content-disposition': "attachment; filename*=UTF-8''%E6%8A%A5%E8%A1%A8.pdf",
      },
    }
    const mockRequest = vi.fn().mockResolvedValue(mockResponse)
    const mockInstance = { request: mockRequest } as any

    await downloadFile('/api/file', { requestInstance: mockInstance })

    expect(saveAs).toHaveBeenCalledWith(expect.any(Blob), '报表.pdf')
  })

  it('should fallback to "download" when no filename is available', async () => {
    const mockResponse = {
      data: new Blob(['file content']),
      headers: {},
    }
    const mockRequest = vi.fn().mockResolvedValue(mockResponse)
    const mockInstance = { request: mockRequest } as any

    await downloadFile('/api/file', { requestInstance: mockInstance })

    expect(saveAs).toHaveBeenCalledWith(expect.any(Blob), 'download')
  })

  it('should prefer explicit filename over Content-Disposition', async () => {
    const mockResponse = {
      data: new Blob(['file content']),
      headers: {
        'content-disposition': 'attachment; filename="server-name.pdf"',
      },
    }
    const mockRequest = vi.fn().mockResolvedValue(mockResponse)
    const mockInstance = { request: mockRequest } as any

    await downloadFile('/api/file', { requestInstance: mockInstance, filename: 'my-file.pdf' })

    expect(saveAs).toHaveBeenCalledWith(expect.any(Blob), 'my-file.pdf')
  })

  it('should pass custom headers', async () => {
    const mockResponse = {
      data: new Blob(['file content']),
      headers: {},
    }
    const mockRequest = vi.fn().mockResolvedValue(mockResponse)
    const mockInstance = { request: mockRequest } as any

    await downloadFile('/api/file', {
      requestInstance: mockInstance,
      filename: 'test.pdf',
      headers: { 'X-Custom': 'value' },
    })

    expect(mockRequest).toHaveBeenCalledWith(
      expect.objectContaining({
        headers: { 'X-Custom': 'value' },
      }),
    )
  })
})
