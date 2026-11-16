# dwy_media 测试用例

测试文件：`test/media_test.dart`。2026-11-16，Flutter3.50.0 / Dart3.14.0，9项测试通过；系统相册、权限和真实设备未验收。

| 测试 | 可判定目标 |
| --- | --- |
| library reads limited assets without requesting broader access | limited 读可见资产；分页0/1正确，无隐式权限请求 |
| denied library does not enumerate or automatically prompt | 拒绝时不列相册；显式请求才调用授权 |
| paging and thumbnail bounds reject invalid input before plugin work | 非法页码、分页大小、缩略图尺寸在插件调用前拒绝 |
| limited manager rechecks state after the system selection | limited管理完成后重新读取权限 |
| missing or cloud-unavailable file is an explicit unavailable result | 资源缺失不伪造本地文件 |
| system picker cancellation stays empty and camera cancellation is null | 系统选择取消与拍照取消保留正常取消语义 |
| system picker preserves files and exposes stream instead of permanent path | 返回可读Dwy资源，支持流与长度 |
| Android lost data has an explicit recovery entry and is not a new pick | 恢复只调用恢复入口，不发起新选择 |
| platform failures retain code and cause without masquerading as cancellation | 相机拒绝/恢复错误保留code和cause，不返回假空结果 |

集成验收：iOS18+与Android10+权限拒绝/limited/全授权、单多图/混合选择、拍照取消、HEIC、iCloud未下载资源、Android低内存Activity销毁后恢复。宿主用官方Flutter CLI生成，真机入口与结果由集成任务记录，不在无SDK环境伪造结果。
