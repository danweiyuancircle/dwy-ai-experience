---
source_url: https://docs.dolphindb.cn/zh/tools/backend_grafana.html
fetched_at: 2026-05-19T09:47:40Z
category: tools
title: DolphinDB Datasource Next
sha1: df3e801200265afb7e443e9d8452fa5323c2214d
---

# DolphinDB Datasource Next

DolphinDB 特别提供了 dolphindb-datasource-next 数据源插件。该插件使用 Go 语言编写，运行在 Grafana 后端，支持用户在 Grafana 面板上实现 DolphinDB 时序数据的可视化。

注意：使用该插件需要 Grafana Server 和数据库部署在同一网络下，或 Grafana Server 可以连接到数据库。

![](grafana/backend1.png)

## 安装方法

### 1. 安装 Grafana

前往 [Grafana 官网](https://grafana.com/oss/grafana/)下载并安装最新的开源版本 (OSS, Open-Source Software)。

### 2. 安装 dolphindb-datasource-next 插件

在 [Github-grafana\_datasource-Releases](https://github.com/dolphindb/grafana-datasource-next/releases) 中下载最新版本的插件压缩包，如 *dolphindb-datasource-next.v1.0.0.zip*。

将压缩包中的 *dolphindb-datasource-next* 文件夹解压到以下路径：

- Windows：*\<grafana 安装目录>\data\plugins\*
- Linux：*/var/lib/grafana/plugins/*

注意：如果不存在 plugins 目录，可手动创建。

在 plugins 目录下，应形成形如以下的文件结构：

```dolphindb
plugins
├── dolphindb-datasource-next
│   ├── LICENSE
│   ├── README.md
│   ├── components
│   ├── go_plugin_build_manifest
│   ├── gpx_dolphindb_datasource_windows_amd64.exe
│   ├── img
│   ├── module.js
│   ├── static
│   └── plugin.json
├── other_plugin_1
├── other_plugin_2
└── ...
```

### 3. 修改 Grafana 配置文件，使其允许加载未签名的 dolphindb-datasource-next 插件

推荐用户阅读 [Grafana 配置说明文档](https://grafana.com/docs/grafana/latest/administration/configuration/#configuration-file-location)，然后打开并编辑配置文件。

在 `[plugins]` 部分下面取消注释 `allow_loading_unsigned_plugins`，并配置为 `dolphindb-datasource-next`。

即把下面的脚本：

```dolphindb
# Enter a comma-separated list of plugin identifiers to identify plugins to load even if they are unsigned. Plugins with modified signatures are never loaded.
;allow_loading_unsigned_plugins =
```

改为：

```dolphindb
# Enter a comma-separated list of plugin identifiers to identify plugins to load even if they are unsigned. Plugins with modified signatures are never loaded.
allow_loading_unsigned_plugins = dolphindb-datasource-next
```

注意：每次修改配置项后，需重启 Grafana。

### 4. 启动或重启 Grafana 进程或服务

推荐用户阅读 [Grafana 快速上手文档](https://grafana.com/docs/grafana/latest/setup-grafana/start-restart-grafana/)。

### 验证已加载插件

若成功安装，可在 Grafana 启动日志中查看类似如下内容：

```dolphindb
WARN [05-19|12:05:48] Permitting unsigned plugin. This is not recommended logger=plugin.signature.validator pluginID=dolphindb-datasource-next pluginDir=<grafana 安装目录>/data/plugins/dolphindb-datasource-next
```

日志文件路径：

- Windows：*\<grafana 安装目录>\data\log\grafana.log*
- Linux：*/var/log/grafana/grafana.log*

或者可访问链接：<http://localhost:3000/plugins>。若成功安装，可看到页面中 DolphinDB 插件是 Installed 状态。

## 使用方法

### 1. 打开并登录 Grafana

打开 [http://localhost:3000](http://localhost:3000/)。初始登入名以及密码均为 admin。

### 2. 新建 DolphinDB 数据源

打开 <http://localhost:3000/datasources> ，或点击左侧导航的 `Connections > Data sources` 添加数据源，搜索并选择 “dolphindb”，配置数据源后点 `Save & Test` 以保存数据源。

### 3. 新建 Panel，通过编写查询脚本或订阅流数据表，可视化 DolphinDB 时序数据

打开或新建 Dashboard，编辑或新建 Panel，在 Panel 的 Data source 属性中选择上一步添加的数据源

#### 3.1. 编写脚本执行查询，可视化返回的时序表格

1. 将 query 类型设置为`脚本`。
2. 编写查询脚本，代码的最后一条语句需要返回 table。
3. 编写完成后按 `Ctrl + S` 保存，或者点击页面中的刷新按钮 (Refresh dashboard)，可以将 Query 发到 DolphinDB 数据库运行并展示出图表。
4. 代码编辑框的高度通过拖动底部边框进行调整。
5. 点击右上角的保存 `Save` 按钮，保存 panel 配置。

dolphindb-datasource-next 插件支持变量，比如:

- `$__timeFilter` 变量: 值为面板上方的时间轴区间，比如当前的时间轴区间是 `2022-02-15 00:00:00 - 2022.02.17 00:00:00` ，那么代码中的 `$__timeFilter` 会被替换为 `pair(2022.02.15 00:00:00.000, 2022.02.17 00:00:00.000)`。
- `$__interval` 和 `$__interval_ms` 变量：值为 Grafana 根据时间轴区间长度和屏幕像素点自动计算的时间分组间隔。`$__interval` 会被替换为 DolphinDB 中对应的 DURATION 类型；`$__interval_ms` 会被替换为毫秒数 (整型)。
- query 变量: 通过 SQL 查询生成动态值或选项列表。

更多变量请查看 [Grafana 变量说明](https://grafana.com/docs/grafana/latest/variables/)。

#### 3.2. 订阅并实时可视化 DolphinDB 中的流数据表

要求：DolphinDB server 版本不低于 2.00.9 或 1.30.21。

1. 将 query 类型设置为`流数据表`。
2. 填写要订阅的流数据表表名。
3. 点击暂存按钮。
4. 将时间范围改成 `Last 5 minutes`（需要包含当前时间，如 Last x hour/minutes/seconds，而不是历史时间区间，否则看不到数据）。
5. 点击右上角的保存 `Save` 按钮，保存 panel 配置。

### 4. Grafana Alerting（警报）的使用

Grafana 警报允许设置告警条件，以监视特定事件或情况。当告警条件被满足后，Grafana 可以通过配置的方式发送通知。

接下来，将通过一个简单的示例介绍警报的使用方法。

1. **查询数据**

   编写一段查询脚本，在 Dashboard 中查询一段数据，比如某一公司的股价。

   ![](grafana/backend2.png)
2. **找到面板下方的 Alert 标签页，并选择创建 Alert**

   ![](grafana/backend3.png)
3. **输入警报名称，并设置用于设置告警条件的相关数据。**

   比如输入时间和股价。

   ![](grafana/backend4.png)
4. **设置告警条件**

   比如设置当最高价大于 180 时告警。

   ![](grafana/backend5.png)
5. **设置查询评估行为**

   比如设置每 10 秒就查询一次，并且在这种情况持续 10 秒后告警。

   ![](grafana/backend6.png)  
   ![](grafana/backend7.png)
6. **（可选）设置通知方式**

   此处设置了发送邮件作为通知方式，Grafana 支持多种通知方式，比如 Slack, Discord, Webhook, Wecom, DingDing 等。

   ![](grafana/backend8.png)
7. **保存警报并退出**

   ![](grafana/backend9.png)
8. **检查效果**

   ![](grafana/backend10.png)  

   当告警条件满足时，警报被触发。警报的状态变为 Firing，并且 Panel 的状态变为“alerting”，在 Panel 旁边的图标将显示为一个红色的告警图标。

### 5. 参考文档，进一步学习 Grafana 使用

[Grafana 官方文档](https://grafana.com/docs/grafana/latest/)。

### FAQ

Q：如何设置 Dashboard 自动刷新间隔？
A：对于脚本类型，打开 Dashboard，在右上角刷新按钮右侧点击下拉框选择“自动刷新间隔”；对于流数据表类型，数据是实时的，无需设置。

如果需要自定义刷新间隔，可以打开 `dashboard settings > Time options > Auto refresh`，输入自定义的间隔。
如果需要定义比 5s 更小的刷新间隔，比如 1s，需要按下面的方法操作：

1. 修改 Grafana 配置文件：

   ```dolphindb
   [dashboards]
   min_refresh_interval = 1s
   ```
2. 修改完后重启 Grafana。

(参考回复：[How to change refresh-rate from 5s to 1s](https://community.grafana.com/t/how-to-change-refresh-rate-from-5s-to-1s/39008/2) )

## 构建及开发方法

```dolphindb
# 安装最新版的 nodejs
# https://nodejs.org/en/download/current/
git clone https://github.com/dolphindb/grafana-datasource-next.git
cd grafana-datasource-next
# 安装项目依赖
npm i
# 开发
npm run dev
# 构建
npm run build
mage
# 完成后产物在 dist 文件夹中。将 out 重命名为 dolphindb-datasource-next 后压缩为 .zip 即可
```
