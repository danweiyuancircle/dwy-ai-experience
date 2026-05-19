---
topic: functions-string
source_files:
  - official/funcs/funcs_by_topics.md
  - official/progr/data_mani/string_obj.md
  - official/progr/data_mani/string_oper.md
  - official/progr/data_mani/create_strings.md
  - official/progr/data_mani/search_in_string.md
  - official/progr/data_types.md
  - official/funcs/s/substr.md
  - official/funcs/s/strReplace.md
  - official/funcs/s/string.md
  - official/funcs/s/symbol.md
  - official/funcs/c/concat.md
  - official/funcs/c/char.md
generated_at: 2026-05-19
---

# 字符串函数

## 何时用此主题

用户问"DolphinDB 字符串怎么截取/拼接/替换"、"SYMBOL 和 STRING 选哪个"、"股票代码加交易所后缀"、"中文字符串长度"、"正则匹配"、"GBK 与 UTF-8 转码"、"字符串类型超长报错"等场景。DolphinDB 字符串默认 UTF-8 编码。

## 字符串类型选择

| 类型 | 上限 | 适用 | 注意 |
|---|---|---|---|
| SYMBOL | 255 字节 | 短编码、重复值多（股票代码、交易所、品种） | **超 255 字节抛异常**；单分区不同取值数须 < 2,097,152（2^21）；UTF-8 中文 1 字 = 3 字节 |
| STRING | 65,535 字节（64 KB - 1） | 中等文本、描述字段 | 写分布式库超限**静默截断**到 65,535 字节 |
| BLOB | 67,108,863 字节（64 MB - 1） | 大文本、二进制 | **不支持任何计算**；写分布式库超限**静默截断** |
| CHAR | 1 字节 | 单字符（ASCII） | 单引号字面量 `'a'` 默认是 CHAR 不是 STRING；`char("990")` 会失败 |

SYMBOL 优势：排序比 STRING 快 ~26×，布尔运算快 ~9×（官方实测 300 万记录）。但只在"重复多 + 经常被排序/搜索/比较"时才用，描述性字段不要用。

## 常用函数速查

### 创建 / 转换

| 函数 | 用途 |
|---|---|
| `string(X)` | 任意类型 → STRING；`string()` 返回 `""` |
| `symbol(X)` | STRING 向量 → SYMBOL 向量 |
| `char(X)` | 整数（ASCII 码） → CHAR；不支持多字符字符串 |
| `charAt(s, i)` | 取第 i 位字符，返回 CHAR（位置从 0 起） |
| `toCharArray(s)` | 字符串 → CHAR 向量 |
| `format(X, fmt)` / `decimalFormat` / `temporalFormat` | 按格式串生成字符串 |
| `stringFormat` | C 风格 printf |

字面量：双引号 `"x"`、反引号 `` `x ``、单引号 `'x'`（单引号是 CHAR）。反引号不能含空格，多元素反引号写成 `` `IBM`MSFT`GOOG ``。

### 提取 / 截取

| 函数 | 用途 |
|---|---|
| `left(s, n)` / `right(s, n)` | 左/右取 n 个字符 |
| `substr(s, offset, [length])` | 从 offset 起截 length 个；offset 从 0 起，length 越界自动到尾 |
| `substru(s, offset, [length])` | 同 substr 但按 UTF-8 字符（非字节）切，**中文用这个** |
| `strlen(s)` | 字符串字节长度 |
| `strlenu(s)` | UTF-8 字符数（**中文用这个**） |
| `wc(s)` | 单词数 |

### 大小写 / 修剪 / 填充

`lower / upper / initcap`（首字母大写）；`ltrim / rtrim / trim`（去空格）；`strip`（去空格 + tab + 换行 + 回车）；`lpad / rpad`（左/右补到指定长度）；`repeat(s, n)`（重复 n 次）。

### 搜索 / 判断

| 函数 | 用途 |
|---|---|
| `like(s, pat)` / `ilike` | SQL LIKE 模式（`%`/`_`），ilike 不区分大小写 |
| `strpos(s, sub)` | 子串首次出现位置，找不到返回 -1（位置从 0 起），**性能高于 regexFind** |
| `startsWith(s, p)` / `endsWith(s, p)` | 前缀/后缀判断 |
| `regexFind(s, pat, [start])` | 正则匹配，返回起始位置 |
| `regexFindStr(s, pat)` | 正则匹配，返回匹配子串 |
| `regexCount(s, pat, [start])` | 正则匹配出现次数 |
| `isAlpha / isAlNum / isDigit / isNumeric / isUpper / isLower / isTitle / isSpace` | 字符类判断 |

### 替换

| 函数 | 用途 |
|---|---|
| `strReplace(s, pat, rep)` | 普通字符串替换（**所有出现**） |
| `regexReplace(s, pat, rep, [start])` | 正则替换；可指定起始位置 |
| `replace(X, old, new)` | 通用替换（非字符串专用） |

### 分割 / 拼接

`split(s, sep)` 按分隔符切；`concat(X, Y)` 拼接（X 为向量时 Y 作分隔符，`concat(\`a\`b\`c, ",")` → `"a,b,c"`）；运算符 `+` 拼接多串：`var1 + ", " + var2`。

### 编码 / 哈希

`convertEncode(s, from, to)`、`fromUTF8(s, target)`、`toUTF8(s, source)`（支持 GBK 等）；`md5 / gmd5 / crc32`。

## 典型用法

```dolphindb
// 1. 股票代码加交易所后缀（沪市 6 开头）
symbols = `000001`600000`300750
withSuffix = each(def(x): x + iif(left(x,1)=="6", ".XSHG", ".XSHE"), symbols)
// → ["000001.XSHE","600000.XSHG","300750.XSHE"]

// 2. SYMBOL 长度校验（UTF-8 字节）
codes = ["AAPL", "中文超长描述字符串"]
oversize = strlen(codes) > 255
// strlen 按字节算，中文每字 3 字节

// 3. 中文按字符截取（不要用 substr 按字节切，会乱码）
substru("你好世界 DolphinDB", 0, 4)  // → "你好世界"

// 4. CSV 导入 GBK 编码
loadTextEx(dbHandle, `t, `date, "data.csv", , , , , encoding="GBK")

// 5. 批量正则提取（从日志抽 IP）
logs = ["[2024] 192.168.1.1 GET /api", "[2024] 10.0.0.5 POST /x"]
ips = regexFindStr(logs, "\\d+\\.\\d+\\.\\d+\\.\\d+")

// 6. 表中字符串列拼接（SQL 上下文）
select symbol + "_" + string(date) as key from t

// 7. SYMBOL 反引号字面量
ex = `XSHG`XSHE`XBSE        // SYMBOL VECTOR，等价于 symbol(["XSHG","XSHE","XBSE"])

// 8. 按管道符切分行情快照
parts = split("XOM|2018.02.15|76.21", "|")  // → ["XOM","2018.02.15","76.21"]
```

## 常见陷阱

- **SYMBOL 上限 255 字节，超限抛异常**（与 STRING/BLOB 静默截断不同），UTF-8 中文 1 字 = 3 字节，按字节算
- **单分区 SYMBOL 不同取值不能超过 2,097,152**，否则报 `"One symbase's size can't exceed 2097152"`
- **CHAR ≠ STRING**：`'A'` 是 CHAR，`"A"` 和 `` `A `` 是 STRING；要把 CHAR 转 STRING 用 `string('A')`
- **中文截取用 `substru` / `strlenu`**：`substr` 和 `strlen` 都按**字节**算，中文 UTF-8 占 3 字节会切坏字符
- **`strpos` 性能优于 `regexFind`**，无需正则时不要用 regexFind
- **BLOB 不支持任何计算**：不能 split/concat/strReplace；做处理前转 STRING
- **`char(X)` 只接 ASCII**：`char("990")` 会失败；想转字符向量用 `toCharArray`
- **`strReplace` 替换所有出现**，不像某些语言只换第一个
- **反引号字面量不能含空格**：`` `Hello World `` 是两个元素 `["Hello","World"]`
- **写入 STRING/BLOB 超限静默截断**，不报错；批量入库前应校验长度
- **描述性字段（文章正文、备注）不要用 SYMBOL**：哈希表占内存，重复率低反而拖慢

## 下钻原文

- 字符串总览：`official/progr/data_mani/string_obj.md`
- 字符串操作示例：`official/progr/data_mani/string_oper.md`
- 创建与格式化：`official/progr/data_mani/create_strings.md`
- 搜索匹配：`official/progr/data_mani/search_in_string.md`
- 数据类型上限与 SYMBOL 约束：`official/progr/data_types.md`
- 函数完整清单（按主题"字符串"）：`official/funcs/funcs_by_topics.md`
- 单函数详细签名：`official/funcs/{首字母}/{name}.md`
