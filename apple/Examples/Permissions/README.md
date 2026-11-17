# 权限宿主示例

这是仓库内源码 QA 工程，和现有 IOSControls 一样使用本地 package；不是业务项目分发模板。消费项目仍按 apple/Docs/Permissions.md 选择已发布语义化 tag。

在仓库根执行 `xcodegen generate --spec apple/Examples/Permissions/project.yml --project apple/Examples/Permissions`，打开生成工程，选择 PermissionsIOS 或 PermissionsMac。iOS 18+、macOS 26+，Swift 6；真实 Mac 权限验收需在 Xcode 中配置自己的签名团队，保留沙盒与摄像头权益。

示例仅在用户点击后申请相机，可选择一个文件并读取最多一个字节；不会读取整份文件。拒绝后的说明使用 PermissionExplanation，打开设置与刷新状态分开。模拟器没有摄像头不代表真实设备已允许；本工程不重置隐私权限，不申请完整磁盘访问。

人工验收：首次申请允许/拒绝；重新进入页面无自动重复请求；设置中变更后刷新得到实际状态；取消文件选择不触发读写；所选文件可读取；关闭 Mac 窗口释放引导。测试结果须逐项记录，源码编译通过不能替代真实系统弹框与无障碍验收。
