# AuthCore 回归清单

- AuthSessionStoreTests：后端身份、只保存 refresh token、恢复轮换、网络失败退出、迟到登录/刷新撤销新 access、并发刷新合并、永久失效 refresh 清理、旧 access 已失效仍撤销轮换后的新 access、Keychain 删除失败仍尝试服务端撤销、保存失败撤销新会话。
- AppCloudAuthClientTests：保留应用路径前缀、Google body / SUCCESS 信封、空 email、Unicode profile 按字符限长、Bearer logout 无 body、服务错误、拒绝远程 HTTP；默认显式发送系统首选语言，邮箱发码的 zh / zh-*（含简繁与大小写）归一为 Accept-Language: zh，英文、日文、越南文、地区代码、空值及未知语言归一为 en；注入语言来源在同一客户端的每次请求重新读取，宿主切换语言即时生效。
- KeychainRefreshTokenStoreTests：随机测试 namespace 中写入/轮换/删除、同 origin 不同应用隔离、device UUID 持久化与 namespace 隔离。
- Apple 认证：挑战/交换请求保留应用前缀，仅编码约定字段与可选姓名，nonce 原样交原生 provider，畸形挑战/过大材料/失败信封拒绝；重复点击、系统取消、挑战/原生/后端迟到回调、Task 取消与存储失败均不能安装旧会话，已签发凭据按共用路径撤销；原 Google-only 后端无需实现 Apple 协议。

运行：`swift test --filter AuthCoreTests`。

Google SDK 真实 OAuth、宿主 URL scheme、用户取消与后端生产配置需要宿主集成后人工验收；本清单不宣称覆盖。

- AppCloudAuthClientTests：改邮箱独立 Bearer 路由、external/google 重新认证字段、轮换 token 信封、缺省密码不发 null、UUID/密码前端校验、当前身份列表与绑定/解绑精确字段。
- AuthSessionStoreTests：改邮箱复用私有 install 保持 userId 并保存轮换 refresh；A 的迟到响应不能覆盖 B 的会话。
- 管理入口在 B 登录已开始、A 会话仍残留时拒绝发请求；管理响应返回前同时核对 generation、用户和实际 access 会话，同账号 refresh 也使旧响应失效。

## 购买准入与原生第三方登录增量（2026-10-28）

- `AppCloudAuthClientTests.testAdmissionProofIsIncludedForEverySessionExchange`：邮箱登录/注册、Google、Apple external、refresh每次读取并提交准入证明。
- `AppCloudAuthClientTests.testRejectedAdmissionProofNeverSendsCredentials`：空/超长/读取失败证明不能发送身份凭据。
- `AppCloudAuthClientTests`、`AuthSessionStoreTests`：Apple 管理挑战使用当前会话与服务端 nonce，重新认证材料保留授权码；切号或取消后不返回迟到材料。
- `ExternalSessionTests`：第三方返回用户与refresh安装；取消后迟到会话撤销且不污染当前本地状态。
