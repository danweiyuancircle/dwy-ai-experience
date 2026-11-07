---
description: Vue 3 前端开发避坑清单（CSS 动画 / 响应式 / 路由 / 构建 / SSR 踩坑），按分类持续追加
paths:
  - "**/*.vue"
  - "**/*.ts"
  - "**/*.css"
---

# Vue 3 前端开发坑清单

> 动手前先对照本清单避开已知坑；踩到新坑随手按四栏格式（现象 / 根因 / 正确做法 / 适用）追加到对应分类，没有合适分类就新建一个。
>
> 通用开发规范见 `dwy-vue-core` rule，本文件只记**非显而易见的实战坑**。

## 分类索引

- CSS 动画 / 过渡
- 响应式 / 组件（ref / reactive / 生命周期 / props）
- 路由（vue-router / 守卫 / 懒加载）
- 构建 / SSR（Vite / vite-ssg / 预渲染）
- i18n / 内容
- 排查方法论
- 其他分类遇到再加

---

## CSS 动画 / 过渡

### View Transitions 圆形过渡：收回方向（clip-path 缩到 0）收尾闪一帧

- **现象**：用 View Transitions API + `clip-path: circle()` 做主题切换的圆形润开过渡。散开方向（圆 0→大）正常；收回方向（圆 大→0，旧层缩回圆心露出底下新主题）动画走完后页面闪一下。
- **根因**：CSS keyframes 默认 `animation-fill-mode: none`——**动画结束瞬间元素恢复到原始属性值，再等浏览器销毁 VT 伪元素树**。收回方向动画挂在 `::view-transition-old(root)`（旧主题层），从 `circle(175vmax)` 缩到 `circle(0)`；动画一结束，`clip-path` 因 `fill-mode:none` **回弹到无裁切（全屏可见）**，旧主题瞬间全屏重现一帧 → 这就是「闪」。散开方向不闪是因为它的动画挂在 new 层，回弹后的终态（全屏新主题）恰好 == 真实 DOM 态，肉眼看不出。不对称的本质：正在动画的上层，其回弹终态是否等于真实页面态。
- **正确做法**（纯 CSS，不动 JS）：① 给做圆形动画的层加 **`forwards`**，动画结束后保持终态（缩到 `circle(0)` 的层保持不可见），杜绝回弹全屏闪现——这是关键修复；② 给静止的对侧层补一段**恒等铺满动画 + `both`**（`from`/`to` 都是 `circle(175vmax)`），让它整个过渡期间也作为活动合成层，与对侧合成待遇对称，收尾两层合成组同步解散，消除高对比（纯黑↔纯白）下的交接重绘。
  ```css
  @keyframes vt-hold-full {
    from { clip-path: circle(175vmax at var(--vt-x, 50%) var(--vt-y, 50%)); }
    to   { clip-path: circle(175vmax at var(--vt-x, 50%) var(--vt-y, 50%)); }
  }
  html[data-vt-direction='conceal']::view-transition-new(root) {
    z-index: 1; animation: vt-hold-full var(--vt-dur) var(--vt-ease) both;
  }
  html[data-vt-direction='conceal']::view-transition-old(root) {
    z-index: 2; animation: vt-circle-conceal var(--vt-dur) var(--vt-ease) forwards;
  }
  ```
- **适用**：通用。推广教训：① 凡 keyframes 动画**结束态偏离元素静止态**（clip-path / transform / opacity 终值非默认），必须显式 `animation-fill-mode: forwards`（或 `both`），否则结束瞬间回弹一帧；不限 View Transitions。② 高对比色块下任何一帧亮度跳变都肉眼可见，动画收尾要让「正在动画的上层终态 == 真实 DOM 态」。③ 逐帧闪烁靠截图基本抓不到（只在单帧出现），定位靠根因推理 + CSSOM 确认规则生效，别依赖视觉快照验证。

## 响应式 / 组件

<!-- 待填：踩到坑按四栏格式追加 -->

## 路由

<!-- 待填 -->

## 构建 / SSR

<!-- 待填 -->

## i18n / 内容

<!-- 待填 -->

## 排查方法论

<!-- 待填 -->
