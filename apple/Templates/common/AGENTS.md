# __APP_NAME__ Apple 项目规则

所有回答使用中文。修改前读取 `docs/ARCHITECTURE.md` 和受影响清单，保留用户未提交改动，不自动升级基础库、改变系统下限或发布。

## 四层架构

- ① App：本端入口、DI、路由、scene/window 生命周期。
- ② Features：本端业务域页面、页面状态与 BusinessUI。共享 UI 满足需求时直接使用，禁止同功能再包装；业务定制优先组合，缺口可自行实现并收敛到业务组件。
- ③ BizFoundation：`packages/__APP_NAME__Core/Sources/BizFoundation` 保存 UI 无关的业务规则、模型、协议与共享服务；本端产品平台适配按需放 ios/Platform 或 macos/Platform。
- ④ Foundation：AppleAppKit 的实际通用产品，不复制源码，不建立空层锚点。产品平台包不是第五层。

共享核心不得依赖 SwiftUI/UIKit/AppKit、App、DesignKit 或具体平台实现。App 创建平台实现并按协议注入；不把两端 Store、窗口与路由混进共享核心。Feature 不直接访问另一 Feature 内部页面或状态。

## 工程与依赖

- 每端 project.yml 仅收录本端源码，公共业务通过相对 path 的 package product 接入，不手工编译另一端或产品核心源码。
- 业务 Platform 不建包时显式加入本端 sources；独立建包时由本端 Package.swift 定义 target，只通过 product 引用，禁止漏编译和重复编译。
- 外部基础库使用已发布的精确版本。真正直接消费者可分别声明同一依赖，但约束和已有锁文件必须一致；不为版本去重增加转发层。
- iOS/iPadOS 18+；macOS 26+、Apple Silicon arm64。新 API 保留最低系统的可用行为。

## 验证

从产品根执行 `python3 scripts/check-architecture.py`；业务单测执行 `swift test --package-path packages/__APP_NAME__Core`。对应平台先进入 ios 或 macos 执行 `xcodegen generate`，再构建、运行和验证实际入口。iOS 另运行 `python3 -m unittest discover -s ios/Tests -p 'test_*.py'`。

结构检查不能判断所有同功能包装、同 target 引用或生命周期语义，仍需审查；构建、单测、目标系统交互和视觉分别报告，不以其中一项代替其他项。业务 UI 自行实现的系统适配和可访问性由本项目验证。
