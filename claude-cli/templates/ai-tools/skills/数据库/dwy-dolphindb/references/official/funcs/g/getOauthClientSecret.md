---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getOauthClientSecret.html
fetched_at: 2026-05-19T09:25:10Z
category: funcs
title: getOauthClientSecret
sha1: f013fe7dc53bd69bda9371c514a4a89a0b3e5955
---

# getOauthClientSecret

首发版本：3.00.5，3.00.4.1，3.00.3.2

## 语法

`getOauthClientSecret()`

## 详情

获取单点登录（SSO）所使用的 *oauthClientSecret* 配置项的值。仅 admin
用户可调用。当启用配置访问控制（`enableConfigAccessControl=true`）时，由于
*oauthClientSecret* 属于敏感配置项，无法通过 `getConfig`
直接读取，管理员可调用此函数安全地获取该配置。

## 返回值

返回字符串，表示当前系统配置的 *oauthClientSecret* 值。
