import { saveAs } from 'file-saver'
import type { AxiosInstance } from 'axios'

export interface DownloadOptions {
  filename?: string
  method?: 'GET' | 'POST'
  data?: any
  headers?: Record<string, string>
  requestInstance?: AxiosInstance
}

export async function downloadFile(url: string, options: DownloadOptions = {}): Promise<void> {
  const { filename, method = 'GET', data, headers, requestInstance } = options

  // 动态 import axios 仅在没传实例时
  const http = requestInstance ?? (await import('axios')).default

  const response = await http.request({
    url,
    method,
    data,
    headers,
    responseType: 'blob',
  })

  const blob = new Blob([response.data])

  // 尝试从 Content-Disposition header 获取文件名
  const resolvedFilename = filename ?? extractFilename(response.headers?.['content-disposition']) ?? 'download'

  saveAs(blob, resolvedFilename)
}

function extractFilename(disposition: string | undefined): string | undefined {
  if (!disposition) return undefined
  const match = disposition.match(/filename\*?=(?:UTF-8''|"?)([^";]+)"?/i)
  return match ? decodeURIComponent(match[1]) : undefined
}

export function saveBlob(blob: Blob, filename: string): void {
  saveAs(blob, filename)
}

export function formatFileSize(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`
}
