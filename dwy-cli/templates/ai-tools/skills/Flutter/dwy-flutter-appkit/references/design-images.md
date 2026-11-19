# 界面与图片

先按 `version-resolution.md` 确认实际源码；下面的能力需在该源码查到后使用，不默认旧版支持。

## dwy_design

- 查对应源码的 `flutter/docs/design-system.md`、`flutter/packages/dwy_design/lib/dwy_design.dart` 和 `flutter/examples/component_gallery/`；该包的接入说明在设计系统文档，不依赖一个未必存在的包 README。
- 在应用根装配主题，核对浅深主题、品牌、令牌与组件覆盖；需要令牌的组件必须获得对应主题。公开主题类型与消费方 UI 库一致，具体 import 按实际 SDK/依赖确认。
- 已满足需求的共享组件直接使用；产品语义、品牌组合和业务交互留在 Feature 的业务组件中，不逐个再包装同功能组件。任务、controller、焦点和导航的所有权按实际 API 保留给调用方。

## dwy_image

- 查实际版本的 `flutter/packages/dwy_image/README.md`，确认来源类型、加载/错误状态、缩略解码和缓存清理接口。
- 按产品/账户划分缓存 namespace；认证头不能代替账户隔离。同一命名空间的实例约束、退出账号时消费者移除与清理/释放顺序，以该版本契约为准。
- 临时文件保留至解码完成；释放实例不等于删除缓存。私有图片退出清理、重启与原生缓存行为需实际验收，Gallery 预览只证明其覆盖的界面。
