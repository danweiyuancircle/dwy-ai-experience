# 登录凭据

先按 `version-resolution.md` 确认项目是否实际包含 `dwy_sign_in`，再查同份源码的 `flutter/packages/esign-in/README.md`、公开导出及测试；提供商与 API 以该版本为准。

- 本包获取第三方凭据，应用后端验证后换发自家会话；拿到 identity token 不等于自家账户已登录。会话保存、账户绑定和注销策略属于产品。
- Apple 的姓名/邮箱可能仅首次授权返回，不用后续空值覆盖已有用户资料。authorization code 的透传与撤销按实际接口和服务端流程核对。
- Google 的 URL Scheme、客户端标识和平台配置由宿主完成；初始化所有权按实际版本查证，不从上游插件最新示例推断封装接口。
- 用户取消、提供商错误和服务端验证失败分别处理；不得记录 token 或授权码。替身测试不证明 Apple/Google 控制台配置和设备登录已通过。
