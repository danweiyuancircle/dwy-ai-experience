# Changelog

## 0.3.0

- 新增 components、composables、paged-list、status/tone 子入口和显式 style.css，原根 API 保持兼容。
- 收口 quant 与 App Cloud 已复用的管理组合组件，保留 OverviewCard 和 WindowToggle 兼容名。
- usePagedList 合并 error、invalidate、reset、isCurrent 及作用域销毁保护。
- EUI peer 下限调整为 2.7.2，包含标签关联及输入操作可访问性修复；声明生成出现 TypeScript 错误时构建失败。
- 搜索支持持久标签、清空后恢复查询及输入法组合保护；折叠首页保留名称，长文本支持键盘全文提示，表格横向溢出可通过键盘操作并显示提示。
- 新增真实组件交互、跨请求状态及干净 tarball 消费/类型验收。

## 0.2.0

### Changed

- 发布包名保持 `@dwydev/admin-kit`。`@dwydev/admin-shell` 在 npm 上不存在，OIDC 不能创建新包（PUT 返回 404）

- 以 quant-cloud 控制台实战版为基座整体重写：AdminShell 收敛为「meta 驱动 + header-center/extra 插槽」,
  不再内置用户菜单 / 通知 / 主题 chrome（宿主经插槽自行组装,与 quant-cloud 用法一致）
- logoTo / collapsedStorageKey / PageHero 壳级页级双开关 / 面包屑末项去链接 / header 插槽 pointer-events 穿透

### Added

- `CreateAdminShellOptions.menuFilter`:侧栏菜单角色过滤谓词(只裁菜单不动路由)
- `asMenuIcon`:lucide 组件 → eui MenuItem.icon 类型收口
- 自带 vitest 单测(路径归一 / 菜单 order / meta 合并 / menuFilter)

### Removed

- `features`(theme/notifications/userMenu)与 `theme.css` —— 破坏性变更,宿主改经插槽组装

## 0.1.0

### Added

- 初版：`createAdminShell` / `defineAdminModule` 模块装配
- `AdminShell`（基于 eui `EAdminLayout`）+ `#header-extra` + 折叠持久化
- `AdminPageHero` / `AdminBreadcrumb` / `AdminPageHeader`（meta 驱动页头）
- `showInMenu` / `menuKey` / `pageHero` / `breadcrumb` 约定
