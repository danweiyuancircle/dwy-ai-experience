/**
 * EDialog 通用对话框组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * EDialog 通用对话框 Props
 */
export interface EDialogProps {
  /** 自定义 class，透传到内容区 */
  class?: HTMLAttributes['class']
  /** 是否展开，支持 v-model:open */
  open?: boolean
  /** 标题文本 */
  title?: string
  /** 描述文本 */
  description?: string
  /** 是否显示右上角关闭按钮 */
  showClose?: boolean
  /** 最大宽度 CSS 值，优先级高于默认 max-width */
  maxWidth?: string
  /** 是否允许按住标题栏拖拽对话框 */
  draggable?: boolean
  /** 点击遮罩是否关闭 */
  closeOnClickModal?: boolean
  /** 按 Esc 键是否关闭 */
  closeOnPressEscape?: boolean
  /** 是否全屏显示（忽略 maxWidth 与拖拽） */
  fullscreen?: boolean
  /**
   * 关闭时是否卸载内容与 overlay。
   * 对齐 reka-ui 2.10 DialogRoot.unmountOnHide：true 关闭即卸 DOM，避免残留 overlay 挡点击；
   * false 仅隐藏，保留状态（SEO / 避免反复挂载）。
   */
  destroyOnClose?: boolean
  /** 是否渲染背景遮罩层（含背景模糊），默认 true；设为 false 时弹框无遮罩，背景内容完全可见可交互 */
  showOverlay?: boolean
}

/**
 * EDialog 通用对话框事件
 */
export interface EDialogEmits {
  /** 展开状态变化 */
  'update:open': [value: boolean]
  /** 打开时触发 */
  open: []
  /** 关闭时触发 */
  close: []
}
