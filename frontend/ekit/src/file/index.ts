/**
 * 文件下载 / Blob 保存 / 文件大小格式化工具
 * 基于 file-saver；支持自动从响应头 Content-Disposition 解析文件名，不需要手动拼接 a[download]
 */
import { saveAs } from 'file-saver'
import type { AxiosInstance } from 'axios'

/**
 * 文件下载配置
 */
export interface DownloadOptions {
  /** 下载文件名；缺省时尝试从 Content-Disposition 解析，再回退为 'download' */
  filename?: string
  /** 请求方法，默认 GET */
  method?: 'GET' | 'POST'
  /** 请求体数据（POST 时用） */
  data?: any
  /** 自定义请求头（如业务需要的 token） */
  headers?: Record<string, string>
  /** 自定义 axios 实例；不传则动态 import 默认 axios，避免本模块强制依赖 axios */
  requestInstance?: AxiosInstance
}

/**
 * 请求并下载文件（二进制）
 * 通过 responseType: 'blob' 拿到二进制，再交给 file-saver 触发浏览器下载
 * @param url 下载地址
 * @param options 下载配置（方法/参数/文件名/请求实例）
 */
export async function downloadFile(url: string, options: DownloadOptions = {}): Promise<void> {
  const { filename, method = 'GET', data, headers, requestInstance } = options

  // 没传实例时才动态 import axios，保证没有下载需求的项目不打包 axios
  const http = requestInstance ?? (await import('axios')).default

  const response = await http.request({
    url,
    method,
    data,
    headers,
    responseType: 'blob',
  })

  const blob = new Blob([response.data])

  // 优先使用用户指定的文件名，其次解析 Content-Disposition，最后兜底
  const resolvedFilename = filename ?? extractFilename(response.headers?.['content-disposition']) ?? 'download'

  saveAs(blob, resolvedFilename)
}

/**
 * 从 Content-Disposition 响应头解析文件名
 * 兼容 RFC 5987 的 filename*=UTF-8'' 编码和普通 filename= 两种格式
 */
function extractFilename(disposition: string | undefined): string | undefined {
  if (!disposition) return undefined
  const match = disposition.match(/filename\*?=(?:UTF-8''|"?)([^";]+)"?/i)
  return match ? decodeURIComponent(match[1]) : undefined
}

/**
 * 将 Blob 触发为浏览器下载
 * @param blob 要保存的二进制数据
 * @param filename 保存的文件名
 */
export function saveBlob(blob: Blob, filename: string): void {
  saveAs(blob, filename)
}

/**
 * 将字节数格式化为带单位的可读字符串（B/KB/MB/GB/TB）
 * @param bytes 字节数
 * @param decimals 小数位，默认 2
 * @returns 如 '1.23 MB'
 */
export function formatFileSize(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`
}
