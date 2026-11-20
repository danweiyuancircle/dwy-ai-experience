# 界面与图片

先按 `version-resolution.md` 确认实际源码；下面的能力需在该源码查到后使用，不默认旧版支持。

## dwy_design

- 查对应源码的 `flutter/docs/design-system.md`、`flutter/packages/dwy_design/lib/dwy_design.dart` 和 `flutter/examples/component_gallery/`；该包的接入说明在设计系统文档，不依赖一个未必存在的包 README。
- 应用根使用独立包 `CupertinoApp` 和 `DwyTheme.create`。浅深色默认跟随系统，品牌色与字体按应用装配，令牌有项目级配置时通过 `DwyTheme.withTokens` 放在根 `builder`。核对实际依赖版本的 API。
- 共用按钮、表单输入、设置项、状态、确认与 Sheet 使用 DWY 入口。导航栏、Tab、滚轮等直接用独立 Cupertino 控件，继承同一套主题。业务交互留在项目 Feature 或应用共享 UI，数据、控制器、焦点和导航由消费方负责。

## dwy_image

- 查实际版本的 `flutter/packages/dwy_image/README.md`，确认来源、缩略解码与缓存接口。默认占位、加载和重试采用 Cupertino，项目可按需传自定义 builder。
- 按产品/账户划分缓存 namespace；认证头不能代替账户隔离。同一命名空间的实例约束、退出账号时消费者移除与清理/释放顺序，以该版本契约为准。
- 临时文件保留至解码完成；释放实例不等于删除缓存。私有图片退出清理、重启与原生缓存行为需实际验收，Gallery 预览只证明其覆盖的界面。
