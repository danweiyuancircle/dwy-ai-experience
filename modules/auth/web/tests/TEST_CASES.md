# 管理员 Web 认证测试清单

- `tests/api.test.ts`（13）：同源 Cookie、禁止重定向/缓存、无 Bearer；backend 注入及跨源/query/hash 拒绝；空值与长度上界；登录错误与会话 401 分流；业务/格式/网络错误；POST 退出及失败处理。
- `tests/session.test.ts`（3）：内存身份及独立实例、凭据不写 localStorage；退出失败保留身份、成功清空；失效阻止迟到恢复。
- `tests/AdminLogin.test.ts`（9）：真实 EUI 表单、品牌、输入上界、错误消息；危险回跳回退首页；合法站内回跳及重复提交；脚本绕过 maxlength 时拒绝超限输入。
- `tests/fixtures/consumer-smoke.mjs`：由 `scripts/smoke-pack.mjs` 在全新目录安装实际 tgz 后执行；导出/API/会话/组件 SSR smoke，不依赖 workspace 源文件。

单元测试的网络被 mock；不代表真实浏览器 Cookie 属性、服务端 CSRF/OAuth 或线上运行验收。
