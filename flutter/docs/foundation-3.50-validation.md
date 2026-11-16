# 非 UI 基础库 Flutter 3.50 验证

日期：2026-11-16。实际工具链为Flutter3.50.0 stable / Dart3.14.0，使用SDK自带CLI。本轮读取并采用团队Dart Skill、官方dart-add-unit-test和dart-run-static-analysis流程；无已连接的Flutter/Dart官方MCP，没有额外安装工具。

## 统一新基线

本次为首次封装，不承担旧版本兼容。8个共享包及Gallery全部声明Dart >=3.14.0；依赖Flutter的成员同时声明Flutter >=3.50.0。纯Dart包不为锁版本引入Flutter。当前固定开发版本仍是3.50.0，不因范围声明而宣称未来版本已验证。

团队Flutter/Dart Skill、基线参考和工作区AGENTS同步约束新库从此版本起步。其他已有产品不在本轮升级范围。UI统一独立material_ui，不保留旧SDK Material入口或无必要的兼容桥。

## 已执行

| 范围 | 命令/结果 |
| --- | --- |
| 依赖 | 完整workspace `flutter pub get`成功 |
| 日志 | `dart test`：13项通过，含脱敏、轮转、flush/export/close交错及故障 |
| 网络 | `dart test`：14项通过，含HTTP、上传、取消、独占下载和诊断隔离 |
| 数据库 | `dart run build_runner build`成功；`dart test`：5项真实磁盘SQLite测试通过 |
| 偏好 | `flutter test`：5项作用域、类型与后端失败测试通过 |
| 安全存储 | `flutter test`：4项账号隔离、清理与失败测试通过 |
| 相册/系统选择器 | `flutter test`：9项权限、分页、读取、取消与丢失数据恢复契约测试通过 |
| 完整工作区 | `flutter analyze`无诊断；受影响代码已格式化 |
| Skills | Flutter/stack发现同步测试7项通过；修改的Flutter入口格式校验通过 |

数据库测试刻意使用锁定Drift remote API检查后台迁移原始错误，导入位置局部标注experimental使用原因，未放宽错误断言或屏蔽产品诊断。

## 检查发现与修复

- Dio新增transformTimeout已穷尽映射为timeout。
- 网络诊断落盘异常不再阻止请求或把成功响应变为失败，独立诊断通道保留原因和栈。
- 日志文件生命周期使用可等待串行输出，避免上游异步定时轮转逃过关闭；flush/prune失败进入明确失败状态，不继续使用已关闭资源。
- 日志URL脱敏覆盖大小写scheme；导出边界解析真实路径，防止路径别名绕过。
- 下载返回独占子目录中的完整文件，不接收可能被其他写入方替换的共享目标文件名；调用方用后删除该子目录。接口为 `Future<File> download(..., parent: Directory)`，无已发布旧接口兼容负担。
- 旧版工具链下限和过期README状态已修订。测试与代码生成依赖沿用工作区已解析的3.50组合，没有新增运行时底座。

## 原生边界

从当前实际解析插件源码回读：shared_preferences Android minSdk24 / iOS13，安全存储Android24 / iOS13，image_picker Android24 / iOS15，photo_manager Android16 / iOS9，均没有要求超过本项目Android29 / iOS18基线。这是声明检查，不能代替原生编译或行为验收。

数据库SQLite原生产物仍需随宿主验证打包；Keychain/Keystore、重启持久化、照片有限权限、云端照片、相机和Android Activity恢复尚未在目标设备验收。网络/日志/数据库使用dart:io，当前封装不支持Web；Web Gallery构建成功不代表这些包可用于浏览器。
