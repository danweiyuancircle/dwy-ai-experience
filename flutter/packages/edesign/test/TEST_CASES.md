# dwy_design 测试用例

| 测试 | 验证内容 |
|---|---|
| `components_test.dart` · uses Cupertino controls and applies shared geometry | 设置列表和按钮使用 Cupertino 控件，应用可覆盖圆角令牌 |
| loading button blocks actions and retains its accessible label | 加载时保留按钮标签，阻止重复操作 |
| search clear updates controller and parent callback | 清空文本并通知调用方，清除入口消失 |
| input exposes form validation without owning application rules | 调用方校验错误显示和恢复，转交自动填充提示并限制输入长度 |
| disabled settings row also blocks its trailing control | 禁用设置行阻止尾部开关操作 |
| confirmation returns explicit choice; dismiss is not acceptance | 取消、确认和点击遮罩各自返回预期结果 |
| bottom sheet scrolls content and returns the explicit result | 模拟键盘遮挡后长内容可滚动，底部动作可达并返回指定结果 |
| settings and status fit a narrow screen with large text | 320 宽、双倍字号下设置和状态组件可布局 |
| `glass_test.dart` · glass bar actions keep their accessible label and callback | 玻璃导航栏图标按钮保留语义标签并触发回调 |
| body sees top padding that includes the glass bar | body 通过 MediaQuery 读到包含玻璃栏的顶部内边距 |
| scaffold without bar items adds no top padding | 没有栏内容时不额外增加顶部内边距 |
| `theme_test.dart` · brand and brightness configure the standalone Cupertino theme | 主题使用独立 Cupertino 类型，品牌与字体可配置 |
| dynamic background follows the active theme | 动态背景跟随浅深主题 |
