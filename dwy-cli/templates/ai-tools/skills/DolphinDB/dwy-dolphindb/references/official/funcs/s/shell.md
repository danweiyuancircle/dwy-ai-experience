---
source_url: https://docs.dolphindb.cn/zh/funcs/s/shell.html
fetched_at: 2026-05-19T09:39:16Z
category: funcs
title: shell
sha1: bab92c3f849dee0405877c0624aebb4e49e1ca87
---

# shell

## 语法

`shell(cmd)`

## 详情

执行操作系统命令。该函数只能在配置参数 enableShellFunction 设置为 true 时，由 DolphinDB
系统管理员执行。

## 参数

**cmd** 是字符串，表示操作系统命令。

## 返回值

若 *cmd* 成功被执行，系统会返回 0。其它返回值请参阅相应操作系统的 `system()` 函数返回值。

## 例子

```dolphindb
cmd="rm -rf /home/user1/test.txt"
shell(cmd);
```
