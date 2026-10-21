# 邮箱密码认证组件实现与验收

日期：2026-10-21。已实现共享库源码，未提交、发布或部署；仓库原有目录迁移和其他未提交改动保留。

## 已实现

- 邮箱作为账号；邮箱＋密码登录。
- 邮箱验证码注册，注册成功自动登录。
- 邮箱验证码重置密码，撤销旧会话并清理本地凭据。
- 可注入的180天滚动refresh策略，活跃刷新顺延；原消费者默认30天固定策略保持。
- iOS SwiftUI `AuthUI` 产品，提供登录、注册、重置页面、中文英文资源、密码/验证码自动填充、密码显隐和键盘退出。
- AuthCore 无需 Google provider 即可使用邮箱认证；现有 Google 构造和接口保留。
- 注册已完成但Keychain失败、取消/退出后的晚回调、并发刷新、短暂断网的状态处理。
- 后端使用事务验证码、HMAC摘要、按应用/用途/邮箱隔离、发送/验证/登录预算及并发密码工作上限。
- 复用eapi Resend传输，不新增Redis；提供旧Google表迁移辅助，保留用户UUID，不静默合并同邮箱身份。

入口：`ios/Sources/iOS/AuthUI/AuthFlowView.swift`。接入指南：`ios/Docs/EMAIL_PASSWORD_AUTH.md`。可运行示例：`ios/Examples/EmailPasswordAuth/`。后端装配与迁移：`modules/auth/backend/README.md`。

密码规则：注册/重置至少15个Unicode标量、最多72个UTF-8字节；不截断、不去空格。邮箱仅去首尾空白和转小写。

## 本地验证

| 验证 | 结果与边界 |
|---|---|
| 共享认证后端完整pytest | 69通过，2跳过；跳过项依赖未配置的PostgreSQL环境 |
| eapi完整pytest | 253通过；2个现有Starlette弃用警告 |
| Swift完整包测试 | 通过；其中AuthCore40项、AuthUI状态10项 |
| 真实iOS SDK编译AuthUI | 通过，arm64 iOS Simulator、部署底线17.0 |
| Xcode示例构建 | 通过 |
| iPhone 17 Pro模拟器XCUITest | 1通过：首次自动呈现、注册/重置导航、输入错误提示 |
| Ruff、格式、diff空格检查 | 通过 |
| 独立wheel安装验收 | 本轮eapi和认证wheel显式安装到全新venv，`python -I`运行完整认证smoke通过，导入来自site-packages |

测试先行记录：AuthUI状态测试先出现16处失败后通过；Keychain注册失败回归先出现3处失败；密码重置迟到响应回归先出现9处失败；示例首次sheet呈现测试先失败再修复；发信延迟剩余TTL先3项失败后修正。

主要命令在仓库根执行：

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift test --disable-automatic-resolution
PYTHONPATH=modules/auth/backend/src:backend/src backend/.venv/bin/python -m pytest modules/auth/backend/tests -q
```

eapi测试在`backend/`执行`.venv/bin/python -m pytest tests -q`。XcodeGen示例测试使用`EmailPasswordAuthExample` scheme。测试环境临时设置DEVELOPER_DIR，没有修改全局xcode-select。

SwiftPM上游Google包存在旧manifest弃用警告与既有未直接使用GoogleUtilities依赖提示，不影响本轮测试和构建。

独立wheel smoke固定核查实际数据库六张表、新邮件传输方法、邮箱注册自动登录/密码登录/重置撤销、180天策略与Google/admin隔离。产物和SHA256证据生成在本机临时验收目录，未上传或发布；本地版本号保持原值，消费端应使用后续正式私有发布产物。

## 审查与兼容性

独立审查发现的两项重要问题均已修复并加回归：注册成功但保存凭据失败的结果区分，以及密码重置后本地会话/迟到请求清理。验证码剩余有效期也已按投递完成后的数据库截止时间返回。

注册/重置的长密码行为前后端一致。密码校验完成到签发会话之间会复核凭据，防止并发重置后旧密码的在途请求发出新会话。公开限流键只使用可信ASGI peer，不直接相信任意XFF/Forwarded。

长期会话仍使用短access和轮换refresh，不保存密码自动重登。后台不发送保活心跳；长期离线、凭据撤销、轮换响应丢失等情形仍可能需要重新登录，符合“活跃用户基本无需重登”的范围，不承诺永不失效。

## 消费端接入前提

本轮未发布私有包、未执行app-cloud生产数据库迁移或部署，也未修改ADBox客户端。启用前需要：

1. 分发匹配的本轮eapi与认证包，并让宿主升级实际依赖产物。
2. 在宿主独立Alembic历史执行邮箱认证表迁移。
3. 注入邮件provider、验证码HMAC密钥和滚动会话策略；Resend配置仅在服务端。
4. ADBox引用包含AuthUI的SwiftPM版本，接入自己的URL/namespace/会话与页面入口。
5. 验收真实Resend邮件、生产PostgreSQL并发/迁移、实际App注册与长期恢复。

示例默认后端`https://api.example.com/adbox`只是配置占位，模拟器页面测试没有冒充真实收信或ADBox业务端验收。
