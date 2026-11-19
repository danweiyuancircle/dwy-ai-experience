# dwy_permission 测试用例

对应 `test/permission_test.dart`（门面契约，Fake adapter）与
`test/plugin_adapter_test.dart`（默认门面对 `permission_handler` 平台实现的映射）。
系统权限框、Info.plist 与 Android Manifest 由宿主真机验收，不在本包测试范围。

## 门面（permission_test.dart）

| 用例 | 验证点 |
| --- | --- |
| status reads without requesting | `status` 只读当前状态，不调用 `request` |
| denied status does not open a prompt until request | 拒绝状态不弹请求；显式 `request` 才进入授权 |
| permanentlyDenied is only a request result | 查询仍可再次请求；请求结果为永久拒绝时 `canAskAgain` 为 false |
| limited and provisional access can still be used | limited / provisional 可用；restricted 不可用且不能再问 |
| platform failures keep the plugin code | `PlatformException.code` 原样进入 `DwyPermissionException` |
| settings open is explicit and does not request | 打开设置不附带请求 |

## 平台映射（plugin_adapter_test.dart）

| 用例 | 验证点 |
| --- | --- |
| maps plugin statuses and the camera permission | 六种 `PermissionStatus` 一一映射；相机查询走 `Permission.camera`，不请求 |
| request uses the plugin request and does not check first | 通知请求走 `Permission.notification`，不先查状态 |
