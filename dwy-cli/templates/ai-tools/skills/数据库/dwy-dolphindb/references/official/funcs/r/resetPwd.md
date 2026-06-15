---
source_url: https://docs.dolphindb.cn/zh/funcs/r/resetPwd.html
fetched_at: 2026-05-19T09:36:11Z
category: funcs
title: resetPwd
sha1: 7b79d90433b468aeb161a3516b9de8bc795b1f55
---

# resetPwd

## 语法

`resetPwd(userId, newPwd)`

## 详情

重置用户的密码。

注：

该函数只能由管理员在控制节点、数据节点和计算节点运行。

## 参数

**userId** 表示用户名的字符串。

**newPwd** 表示用户新密码的字符串。它不能包含空格或控制字符。

从 2.00.10.10 开始，用户可以通过配置项 *enhancedSecurityVerification*
控制是否对 *newPwd* 进行复杂性校验。若不设置 *enhancedSecurityVerification*，则不校验；若设置
*enhancedSecurityVerification*=true，则要求新密码必须满足以下条件：

- 字符个数为8~20
- 至少包含一个大写字母
- 至少包含以下字符之一：!"#$%&'()\*+,-./:;<=>?@[]^\_`{|}~。

## 例子

```dolphindb
resetPwd("AlexEdwards", "T51pm363.");
```
