import type { HTMLAttributes } from 'vue'

export interface UploadFile {
  uid: string
  name: string
  status: 'ready' | 'uploading' | 'success' | 'error'
  url?: string
  raw?: File
  progress?: number
}

export interface EUploadProps {
  class?: HTMLAttributes['class']
  modelValue?: UploadFile[]
  action?: string
  accept?: string
  multiple?: boolean
  limit?: number
  disabled?: boolean
  listType?: 'text' | 'picture' | 'picture-card'
  drag?: boolean
}

export interface EUploadEmits {
  (e: 'update:modelValue', files: UploadFile[]): void
  (e: 'change', files: UploadFile[]): void
  (e: 'exceed', files: File[]): void
  (e: 'remove', file: UploadFile): void
}
