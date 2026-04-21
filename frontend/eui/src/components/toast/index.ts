/**
 * EToast 全局消息通知组件导出入口
 * EToast 作为容器挂载一次；业务代码通过 useToast 发出通知
 */
export { default as EToast } from './EToast.vue'
export type { EToastProps } from './types'
export { useToast } from './useToast'
