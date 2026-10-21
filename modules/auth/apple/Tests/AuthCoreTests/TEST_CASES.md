# AuthCore 回归清单

- AuthSessionStoreTests：后端身份、只保存 refresh token、恢复轮换、网络失败退出、迟到登录/刷新撤销新 access、并发刷新合并、永久失效 refresh 清理、旧 access 已失效仍撤销轮换后的新 access、Keychain 删除失败仍尝试服务端撤销、保存失败撤销新会话。
- AppCloudAuthClientTests：保留应用路径前缀、Google body / SUCCESS 信封、空 email、Unicode profile 按字符限长、Bearer logout 无 body、服务错误、拒绝远程 HTTP。
- KeychainRefreshTokenStoreTests：随机测试 namespace 中写入/轮换/删除、同 origin 不同应用隔离、device UUID 持久化与 namespace 隔离。

运行：`swift test --filter AuthCoreTests`。

Google SDK 真实 OAuth、宿主 URL scheme、用户取消与后端生产配置需要宿主集成后人工验收；本清单不宣称覆盖。
