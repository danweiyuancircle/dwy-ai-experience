# 管理框架与组合组件测试

- `create-admin-shell.test.ts`：原根 API、菜单/路由装配、排序和过滤合同。
- `components/TEST_CASES.md`：原外壳及迁入组件、OverviewCard 兼容入口、真实 EUI 表格/配置/搜索交互。
- `composables/usePagedList.test.ts`：原 quant 分页、搜索、排序及请求竞争。
- `composables/usePagedList-lifecycle.test.ts`：App Cloud 的错误、重试、主动失效和旧响应保护。
- `composables/usePagedList-reset.test.ts`：重置、保留数据/错误、scope 清理和附属汇总提交边界。
- `fixtures/consumer-types.ts`、`fixtures/consumer-smoke.mjs`：实际 tgz 子入口/类型、同一 Vue 作用域及真实 EUI SSR；由 `scripts/smoke-pack.mjs` 执行。

包内测试不证明 registry 已发布、生产已部署或浏览器端所有交互已验收。
