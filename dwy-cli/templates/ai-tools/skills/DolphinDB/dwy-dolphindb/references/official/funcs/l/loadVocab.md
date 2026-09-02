---
source_url: https://docs.dolphindb.cn/zh/funcs/l/loadVocab.html
fetched_at: 2026-05-19T09:30:12Z
category: funcs
title: loadVocab
sha1: 73d56b9b26c3219c895ba921cef12768b724b0c1
---

# loadVocab

首发版本：3.00.4，3.00.3.1

## 语法

`loadVocab(filePath, vocabName)`

## 详情

将指定路径下的词库加载到内存中，用于文本向量化处理。

## 参数

**filePath** 字符串标量，词库文件的路径，可以是相对路径或绝对路径。

**vocabName** 字符串标量，用于指定加载后词库的名称。

## 返回值

无。

## 例子

```dolphindb
loadVocab("/home/data/vocab.txt", "vocab1")
```

相关函数：[unloadVocab](../u/unloadVocab.html), [tokenizeBert](../t/tokenizeBert.html)
