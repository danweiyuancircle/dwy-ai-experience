# Vue 版本与源码定位

1. 从实际消费应用或 workspace 成员出发，查 `package.json`、项目锁文件及 `pnpm-workspace.yaml`；同时核对 catalog、overrides、workspace/link/file、补丁与构建别名。声明范围与 catalog 只是约束，不是安装结果。
2. 从该调用方的解析上下文定位包公开入口，再定位实际包根目录；pnpm 下跟随符号链接确认真实目标。不要仅检查 monorepo 根目录的同名包，不假定 Node 和 Vite alias 指向同一份代码。
3. 通过实际文件路径读取包根 `package.json`，核对 name、version、exports、types、peerDependencies 与相关源码/产物。不要依赖 `require('@dwydev/eui/package.json')` 等未公开子路径，包的 exports 可能禁止访问；dist manifest 同样应从实际文件路径读取。
4. registry 依赖核对锁定版本和来源；Git 依赖核对锁定提交与子目录；workspace/link/file 核对实际源码、提交、相关未提交修改及构建产物；patch 依赖同时读生效补丁。同版本号不能证明代码相同，源码已改也不能证明消费方使用的 dist 已重新构建。

以项目实际解析的声明和运行代码为先，manifest 仅用于导航；缺少 manifest 不等于版本较旧，也可能是源码依赖或产物不完整。公开 API 从 exports/types 及其声明定位，不使用未导出的内部接口。

只有实际包内资料不足时，再查对应发布版本/tag 或锁定提交的仓库源码；旁边的 dwy-shared checkout 必须确认同源同提交，不能因目录存在就使用。包未安装或锁文件与解析目录不一致时，说明缺口，按项目授权的依赖安装/构建流程核对后继续；不自动升级、删锁文件或加 overrides 来匹配文档。

各包独立确认；EUI、EKIT、Admin Kit 与 Auth Web 的版本号没有统一对应关系。组合使用时查实际 peer 约束与主题、样式、Provider、响应及 Cookie 契约，缺少能力时不从另一个版本复制 API。

引用资料的版本线只作导航，带下限的能力在旧版本视为不可用；无版本标签的描述也需查实际接口。项目包管理器/Node、框架工具链、包兼容范围与实际浏览器验证分开报告，不输出凭据。
