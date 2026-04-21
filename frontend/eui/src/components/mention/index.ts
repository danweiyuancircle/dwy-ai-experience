/**
 * EMention @提及输入组件的导出入口
 * 在 textarea 中输入 @ 前缀时弹出候选列表，支持键盘导航
 */
export { default as EMention } from './EMention.vue'
export type { EMentionProps, EMentionEmits, MentionOption } from './types'
