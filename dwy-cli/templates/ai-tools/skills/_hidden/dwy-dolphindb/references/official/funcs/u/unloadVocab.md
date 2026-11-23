---
source_url: https://docs.dolphindb.cn/zh/funcs/u/unloadVocab.html
fetched_at: 2026-05-19T09:43:09Z
category: funcs
title: unloadVocab
sha1: 833501b90d4b9a95a0e6cbb29cef30dbe3e59b9b
---

# unloadVocab

首发版本：3.00.4，3.00.3.1

## 语法

`unloadVocab([vocabName])`

## 详情

从内存中删除已加载的词库。

## 参数

**vocabName** 可选参数，字符串标量，指定要删除的词库名称。若不指定，则删除所有词库。

## 返回值

无。

## 例子

```dolphindb
unloadVocab("vocab1")
```

相关函数：[loadVocab](../l/loadVocab.html), [tokenizeBert](../t/tokenizeBert.html)
