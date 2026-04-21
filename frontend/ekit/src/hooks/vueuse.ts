/**
 * 从 @vueuse/core 精选再导出的常用 hook
 * 避免业务方各自直接依赖 @vueuse/core，统一从 ekit 入口引入；名称与 VueUse 保持一致（useThrottle 映射 useThrottleFn）
 */
export { useThrottleFn as useThrottle } from '@vueuse/core'
export { useWindowSize } from '@vueuse/core'
export { useMediaQuery } from '@vueuse/core'
export { useIntersectionObserver } from '@vueuse/core'
export { useResizeObserver } from '@vueuse/core'
