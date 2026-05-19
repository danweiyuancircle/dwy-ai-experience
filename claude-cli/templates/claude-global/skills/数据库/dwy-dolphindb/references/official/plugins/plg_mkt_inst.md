---
source_url: https://docs.dolphindb.cn/zh/plugins/plg_mkt_inst.html
fetched_at: 2026-05-19T09:45:28Z
category: plugins
title: 在插件市场安装插件
sha1: d9edfb711400a333e6ed8313fb6bae32b2aabb62
---

# 在插件市场安装插件

## 1. 版本要求

- DolphinDB Server: 2.00.10 及更高版本

## 2. 安装 zip 插件（可选）

从插件仓库获取并安装插件前，确保已安装 zip 插件。如已安装，跳过此节。

zip 插件安装方法如下：

1. 下载[zip 插件压缩包](script/zip.zip)
2. 解压 zip 插件压缩包至本地路径。例如：*/path\_to\_DolphinDB\_Server/plugins/zip*。
3. 登录 DolphinDB 客户端后，使用 [loadPlugin](../funcs/l/loadPlugin.html) 命令加载 zip 插件：

   ```dolphindb
   loadPlugin("zip")
   ```

## 3. 安装步骤

1. 在 DolphinDB 客户端中使用 [listRemotePlugins](../funcs/l/listRemotePlugins.html) 命令查看插件仓库中的插件信息。

   ```dolphindb
   login("admin", "123456")
   listRemotePlugins()
   ```
2. 使用 [installPlugin](../funcs/i/installPlugin.html) 命令获取插件描述文件及插件的二进制文件以完成插件安装。以 MySQL 插件为例：

   ```dolphindb
   installPlugin("mysql")
   ```

   返回：`<path_to_MySQL_plugin>/PluginMySQL.txt`
3. 使用 [loadPlugin](../funcs/l/loadPlugin.html) 命令加载插件（即上一步返回的 .txt 文件）。以 MySQL 插件为例：

   ```dolphindb
   loadPlugin("mysql")
   ```

   **注意**：若使用 Windows 插件，加载时必须指定绝对路径，且路径中使用"\\"或"/"代替"\"或""。
