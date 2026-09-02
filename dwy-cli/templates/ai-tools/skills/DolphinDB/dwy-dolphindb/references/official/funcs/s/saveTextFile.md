---
source_url: https://docs.dolphindb.cn/zh/funcs/s/saveTextFile.html
fetched_at: 2026-05-19T09:37:59Z
category: funcs
title: saveTextFile
sha1: 0f58dc27b5d9d399f517b64f8389e26b8d34c47f
---

# saveTextFile

## 语法

`saveTextFile(content, filename, [append=false],
[lastModified])`

## 详情

通过追加或覆盖将字符串保存到文件中。该函数必须要用户登录后才能执行。

## 参数

**content** 是要写入文件的内容。

**filename** 是要保存的文件名。仅支持 CSV 格式的文件。若传入其他格式文件，则无法保证数据准确性。

**append** 是一个布尔值。True 表示追加，False表示覆盖。

**lastModified** 是最后修改的时间，显示的是1970年1月1日零时开始的秒数。

## 例子

```dolphindb
saveTextFile("1234567890\n0987654321\nabcdefghijk\n", "/home/test/abc.txt", false, 1495762562671l);

// output
[content of file "/home/test/abc.txt"]
1234567890
0987654321
abcdefghijk
```
