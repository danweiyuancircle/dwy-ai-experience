/**
 * 模态弹框遮罩表面。
 *
 * EDialog 从 2.1.0 起用 30% 黑加背景模糊，确认框和命令式 MessageBox
 * 若各自写 bg-black/80，同一产品里弹框遮罩深浅会不一致。
 * 抽屉、侧栏、图片灯箱不是弹框，不引用这份。
 */
export const DIALOG_OVERLAY_SURFACE_CLASS = 'bg-black/30 backdrop-blur-sm'
