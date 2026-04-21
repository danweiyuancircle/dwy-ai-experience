/**
 * EUpload 文件上传组件类型定义
 */
import type { HTMLAttributes } from 'vue'

/** 单个上传文件的状态描述 */
export interface UploadFile {
  /** 前端生成的唯一 id */
  uid: string
  /** 原始文件名 */
  name: string
  /** 上传状态：就绪/上传中/成功/失败 */
  status: 'ready' | 'uploading' | 'success' | 'error'
  /** 上传进度百分比 0-100 */
  percentage?: number
  /** 预览/下载地址（图片预览或服务端返回） */
  url?: string
  /** 原始 File 对象 */
  raw?: File
  /** @deprecated 请使用 percentage */
  progress?: number
}

/** EUpload Props */
export interface EUploadProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 当前文件列表，v-model 绑定 */
  modelValue?: UploadFile[]
  /** 上传目标地址（相对/绝对 URL） */
  action?: string
  /** 原生 accept 属性，限制选择的文件类型 */
  accept?: string
  /** 是否允许多选 */
  multiple?: boolean
  /** 文件数量上限 */
  limit?: number
  /** 单个文件最大大小（MB），超出自动拦截并提示 */
  maxSize?: number
  /** 是否禁用 */
  disabled?: boolean
  /** 列表展示样式：text=文字、picture=含缩略图、picture-card=网格卡片 */
  listType?: 'text' | 'picture' | 'picture-card'
  /** 是否启用拖拽上传区域 */
  drag?: boolean
  /** 上传前校验钩子，返回 false 或 reject 则拦截 */
  beforeUpload?: (file: File) => boolean | Promise<boolean>
  /** 选择后是否立即上传；false 时需调用 submit() 手动提交 */
  autoUpload?: boolean
  /** 上传时附加的请求头 */
  headers?: Record<string, string>
  /** XHR withCredentials（跨域携带 cookie） */
  withCredentials?: boolean
}

/** EUpload Emits */
export interface EUploadEmits {
  /** 文件列表更新，用于 v-model */
  (e: 'update:modelValue', files: UploadFile[]): void
  /** 文件列表变化事件 */
  (e: 'change', files: UploadFile[]): void
  /** 数量超出 limit 时触发；payload 为本次被拦截的原始 File 数组 */
  (e: 'exceed', files: File[]): void
  /** 删除单个文件 */
  (e: 'remove', file: UploadFile): void
  /** 点击预览 */
  (e: 'preview', file: UploadFile): void
}
