# ① App 层

- `@main` 入口、根路由、全局 Store / environment 注入（含 `LifetimeStore`）
- `Info.plist`、与打包相关的配置（`project.yml` 在仓库根）
- `Products.storekit`：本地买断商品，scheme 已挂上
- `ReviewPrompt`：第 3 次进根页弹系统评价框

**不要**在这里堆功能页 → 放到 `Features/<子包>/`。
**不要**写领域算法 → 放到 `BizFoundation/`。
免费产品：去掉 `LifetimeStore` 注入和 `Features/Paywall`。
