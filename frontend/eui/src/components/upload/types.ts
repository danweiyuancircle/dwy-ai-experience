import type { HTMLAttributes } from 'vue'

export interface UploadFile {
  uid: string
  name: string
  status: 'ready' | 'uploading' | 'success' | 'error'
  percentage?: number
  url?: string
  raw?: File
  /** @deprecated Use `percentage` instead */
  progress?: number
}

export interface EUploadProps {
  class?: HTMLAttributes['class']
  modelValue?: UploadFile[]
  action?: string
  accept?: string
  multiple?: boolean
  limit?: number
  /** 单个文件最大大小（MB），超出自动拦截并提示 */
  maxSize?: number
  disabled?: boolean
  listType?: 'text' | 'picture' | 'picture-card'
  drag?: boolean
  beforeUpload?: (file: File) => boolean | Promise<boolean>
  autoUpload?: boolean
  headers?: Record<string, string>
  withCredentials?: boolean
}

export interface EUploadEmits {
  (e: 'update:modelValue', files: UploadFile[]): void
  (e: 'change', files: UploadFile[]): void
  (e: 'exceed', files: File[]): void
  (e: 'remove', file: UploadFile): void
  (e: 'preview', file: UploadFile): void
}
