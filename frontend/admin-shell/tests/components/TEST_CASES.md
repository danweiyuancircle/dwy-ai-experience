# 管理组合组件测试

测试从两个实际消费者迁移，公共重叠用例保留一份；正式 EUI 测试不使用控件 stub。密码策略、分页请求状态机与产品 API 不属于本目录。

| 测试文件 | 覆盖场景 |
| --- | --- |
| `frontend/admin-shell/tests/components/action-link-card/ActionLinkCard.test.ts` | 标题、说明和路径都在链接上 |
| `frontend/admin-shell/tests/components/chart-card/ChartCard.test.ts` | 有说明和右侧插槽时都渲染；没写说明和右侧时不留空位 |
| `frontend/admin-shell/tests/components/config-field/ConfigFieldControl.eui.test.ts` | 字符串输入保留上限并写回当前值；开关通过真实点击写回布尔值 |
| `frontend/admin-shell/tests/components/config-field/ConfigFieldControl.test.ts` | 可选日期留空使用 EUI 中文文案，外部清空不写入今天；小数步进 0.01，避免 0.8 被吸走；体积按传入的换算显示，换单位不改字节；改体积数字时写回字节；字符串带长度上限，布尔走开关；900 秒显示成 15 分钟，换单位不改秒数 |
| `frontend/admin-shell/tests/components/confirm-then/confirmThen.test.ts` | 取消时不执行，也不提示；成功用固定文案提示；成功文案可以用返回值拼；失败用抛出值生成文案，并且不再向上抛 |
| `frontend/admin-shell/tests/components/data-overview/DataOverview.test.ts` | 按无标题指标、分组、入口、插槽、说明排列；空的指标和入口不留空栅格 |
| `frontend/admin-shell/tests/components/metric-grid/MetricGrid.test.ts` | 默认三列，容器包在栅格外面；两列停在两列，五列再到 72rem |
| `frontend/admin-shell/tests/components/paged-table/PagedTable.eui.test.ts` | 展示当前行并从真实分页按钮提交下一页；实际横向溢出才显示滑动提示，滚动区可键盘聚焦且关联提示；固定操作列和单元格插槽透传 |
| `frontend/admin-shell/tests/components/paged-table/PagedTable.test.ts` | 操作槽靠右，不进表格；顶栏按钮留在表格外，单元格插槽进表格；total 大于 0 时分页带默认每页条数；省略每页条数时使用统一默认值 50；没有行时不渲染表格和列名，空态仍在；加载中且没有行时只留加载圈；没写空态时用暂无数据；不传 total 时不渲染分页；翻页和改每页条数原样抛出；表头排序和行点击原样抛出；fill 关掉时表格区不占满剩余高度；showTotal 可关 |
| `frontend/admin-shell/tests/components/record-board/RecordBoard.test.ts` | 四区按说明、筛选、汇总、明细排列；没传说明和汇总时不渲染这两区；展示标签和值，danger 才强调数值 |
| `frontend/admin-shell/tests/components/record-code/RecordCode.test.ts` | 有单号时等宽显示，空值用淡色破折号 |
| `frontend/admin-shell/tests/components/record-ellipsis/RecordEllipsis.test.ts` | 完整可见文本不增加键盘停靠，真实截断才可聚焦查看全文；短横和空值只显示占位 |
| `frontend/admin-shell/tests/components/record-ellipsis/RecordEllipsis.eui.test.ts` | 正式 EUI 提示触发器仅使真实截断文本可聚焦，并保留完整文本可读性；窄屏 Enter 和空格均打开全文，且不误触父级行操作 |
| `frontend/admin-shell/tests/components/record-period/RecordPeriod.test.ts` | 日期框收成内容宽度，且不能清空；点快捷档向外抛，半截区间不抛 |
| `frontend/admin-shell/tests/components/record-profile/RecordProfile.test.ts` | 点返回向外抛，身份卡按标题、徽章、说明、操作排；没有标题时不画身份卡，默认插槽仍在 |
| `frontend/admin-shell/tests/components/record-search/RecordSearch.eui.test.ts` | 输入更新关键词，回车与查询按钮均向页面提交；持久标签关联唯一真实输入 id；清空按钮和手动删空各只提交一次查询；外部重置不额外请求；输入法合成回车不提交 |
| `frontend/admin-shell/tests/components/record-search/RecordSearch.test.ts` | 输入同步关键词，回车和按钮都触发查询 |
| `frontend/admin-shell/tests/components/request-feedback/RequestFeedback.test.ts` | 显示请求错误并通过重试按钮通知页面重新加载；加载中提供可读状态，隐藏旧错误与重试入口 |
| `frontend/admin-shell/tests/components/segmented-filter/SegmentedFilter.test.ts` | 选中新档才抛出，取消选中被忽略；有计数时跟在文案后，0 也显示，并画出左侧名字 |
| `frontend/admin-shell/tests/components/stat-card/StatCard.test.ts` | 没有 to 时只展示，有 to 时是带箭头的链接 |
| `frontend/admin-shell/tests/components/status/StatusBadge.test.ts` | 用描边徽章加上对应档的类；开着和完成走生效色，关掉走停用色，未完成走待办色 |
| `frontend/admin-shell/tests/components/overview-card/OverviewCard.eui.test.ts` | 保留 App Cloud 既有 OverviewCard 组件出口；真实 EUI 静态卡展示内容和图标；真实 RouterLink 导航与默认内容 |

运行命令：`pnpm --filter @dwydev/admin-kit test`。真实制品、类型与消费方验收由包级验证另行覆盖。

`frontend/admin-shell/tests/components/AdminShell.accessibility.test.ts` 验证侧栏折叠后首页链接仍有系统名称与首页用途；未配置 logo 时，链接和非链接品牌区均显示成熟图标作为可见入口。
