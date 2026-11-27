/** 适用于单个页面内容节点的短转场。保留 Vue 的条件渲染与 DOM 生命周期。 */
export interface ETransitionProps {
  /** 淡入淡出、轻微上移或轻微缩放，默认 fade。 */
  preset?: 'fade' | 'slide-up' | 'scale'
  /** 初次挂载时也播放入场动画，默认关闭。 */
  appear?: boolean
}
