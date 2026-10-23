# 共享管理组件首批设计

状态：本文保留首批批准时的设计范围。后续可用性与表单审计将 EUI 基线提升为 2.7.2；经用户授权，EUI 2.7.2、admin-kit 0.3.0 已发行并合入 master。初始“不发布 npm”的约束已被后续授权取代；完整认证 UI 仍只交付后续合同设计。

用户已同意 2026-10-23 的跨仓分析方案；本批仅完成通用管理组件收口、两消费方兼容接入，以及后续认证 Provider 合同设计。完整认证 UI、访问控制新功能、后端改动、发行与部署另批实施。

## 架构与方案

沿用现有 EUI、ekit、admin-kit、auth-web；推荐扩展 admin-kit 而非继续复制组件或新增重叠的 admin-pro 包。产品保留接口、领域 DTO、配置继承与权限校验。

admin-kit 新增 components、composables、status/tone、paged-list 子入口，现有根入口保持兼容。公共管理组合组件以 quant 与 App Cloud 共同源码为主体，明确纳入单方已有且无领域依赖的 RequestFeedback、ChartCard、SegmentedFilter、RecordPeriod。PasswordFields 与 createPasswordRules 暂留 quant，不引入量化 core。

usePagedList 合并两套行为：显式 error、invalidate 保留数据、reset 清数据/筛选/排序/错误、自动作用域销毁、fetcher 的 isCurrent 守卫、旧成功/失败/finally 全部禁止回写。保留既有方法与分页参数。

## 合同与兼容

- PagedListOptions.fetcher(params, request) 的 request 提供 isCurrent(): boolean；单参数 fetcher 继续兼容。
- invalidate() 淘汰旧请求并停止 loading，保留数据与错误；reset() 另清空全部分页与筛选状态。
- components 以 props/events/slots 驱动，不访问 API、Pinia、后端角色或浏览器凭据。
- 两消费方保留 @dwy/components 兼容转出口和旧子路径；quant 密码组件继续原实现。
- EUI 支持基线以两消费方已用的 2.7.1 为准；不保留未经验证的 ^2.2.0 承诺。
- 先制作本地独立 tarball 并验收，不发布 npm，不在产品配置中写死临时绝对路径。
- 两产品现有认证和后端安全行为不变。

## 认证后续合同

保持独立管理员 Cookie 与 quant 用户 JWT 两种模式；UI 只依赖 Provider 动作、安全身份、按能力分组的注册/重置/安全设置。接口、错误码、密码策略、协议、人工验证、导航与持久化由宿主适配。换绑邮箱、Google Web、MFA、管理员注册/找回不算既有跨后端能力。本批只写合同文档，不增加运行时认证接口。

## 验收

先测试再迁移/实现；保留双方组件和真实 EUI 交互测试。验证 reset/error/invalidate/dispose/isCurrent 组合；独立构建、类型声明与子入口；两个产品完整前端测试及构建；实际 tarball 消费、Tailwind 扫描和 Vue/EUI 去重。迁移成功不等于已发布或生产验收。
