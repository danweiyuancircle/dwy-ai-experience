# 权限与媒体

先按 `version-resolution.md` 确认实际源码，再分别查 `flutter/packages/dwy_permission/README.md` 与 `flutter/packages/dwy_media/README.md` 的能力、宿主配置、公开入口及测试。不要按包名推断支持所有平台。

- `dwy_permission` 用于其实际支持的运行时权限；`dwy_media` 用于相册枚举、系统媒体选择器和拍照。按真实入口选能力，不为使用系统选择器额外索取整个相册权限。
- 权限状态不能压成一个 Bool；核对该版本如何表达有限访问、拒绝、永久拒绝与受限，以及查询和申请的差异。打开设置成功不等于获得授权，回到应用后重新查询。
- 按所用能力配置用途文案、Android manifest、编译宏和原生下限；不在启动时统一申请所有权限。宿主缺用途文案可能导致系统直接终止进程，不能靠 Dart catch 补救。
- 媒体选择取消与异常分开处理；核对临时文件寿命、持久化所有权、iCloud 资源及 Android lost data 恢复流程，不把恢复入口存在当作已经接通。
- 两包均不承担产品导航或业务会话。limited 访问、设置往返、取消、进程恢复与真实文件访问按设备验收；Web 预览或插件替身测试不能替代。
