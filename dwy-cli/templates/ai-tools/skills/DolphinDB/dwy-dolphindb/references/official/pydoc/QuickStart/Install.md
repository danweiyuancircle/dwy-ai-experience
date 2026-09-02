---
source_url: https://docs.dolphindb.cn/zh/pydoc/QuickStart/Install.html
fetched_at: 2026-05-19T09:52:40Z
category: pydoc
title: 安装
sha1: 1787023dda1cfb73b0ae6f8a39aa8013751893f1
---

# 安装

在安装 dolphindb 前，请确定已部署 Python 执行环境。若无，推荐使用 [Anaconda Distribution](https://www.anaconda.com/products/distribution) 下载 Python 及常用库。

## 支持版本

dolphindb 的详细版本列表和离线下载链接请参照 [pypi dolphindb](https://pypi.org/project/dolphindb/#files)。下表展示 dolphindb 在不同操作系统中对应支持的 Python 版本号。

| 操作系统 | Python 版本号 |
| --- | --- |
| Windows(amd64) | Python 3.8-3.13 |
| Linux(x86\_64) | Python 3.8-3.13 |
| Linux(aarch64) | Conda 环境下的 Python 3.8-3.13 |
| Mac(x86\_64) | Conda 环境下的 Python 3.8-3.13 |
| Mac(arm64) | Conda 环境下的 Python 3.8-3.13 |

**注意**：为保证正常使用 dolphindb ，您需要同时安装以下依赖库：

- future
- NumPy（版本号不得低于 1.18）
- pandas（版本号不得低于 1.0.0，建议不高于 2.2.0，暂不支持 1.3.0）
- packaging
- 扩展依赖：PyArrow（版本号不得低于 9.0.0）

## 安装示例

目前仅支持通过 `pip` 指令安装 DolphinDB Python API，暂不支持 `conda` 安装。安装示例如下：

```dolphindb
$ pip install dolphindb
```

## 常见问题

**Q1：安装失败，或安装成功后无法导入 dolphindb 包。**

A1：建议检查并重装 whl 包。具体操作如下：

1. 通过 [PyPI](https://pypi.org/) 确认是否存在支持当前操作系统（例如 Linux arm 架构、Mac ARM 等）的 DolphinDB API 安装包。若存在，则将该 whl 包下载至本地。
2. 通过如下命令查看适合当前系统环境支持的 whl 包后缀。

   ```dolphindb
   pip debug --verbose
   ```
3. 根据 Compatible tags 的显示信息，将 DolphinDB 的 whl 包名修改为适合系统架构的名称。以 Mac(x86\_64) 系统为例：安装包名为 "dolphindb-1.30.19.2-cp37-cp37m-macosx\_10\_16\_x86\_64.whl"。但查询到 pip 支持的当前系统版本为10.13，则将 whl 包名中的“10\_16”替换成“10\_13”。
4. 尝试安装更名后的 whl 包。

**Q2：无法导入 dolphindb 包，出现如下错误提示：**

```dolphindb
ImportError:DLL load failed while importing dolphindbcpp:找不到指定的模块。
```

A2：DolphinDB Python API 依赖一些动态库。从报错信息上看，可能是缺失了 msvcp140.dll。按照如下方法安装 Visual C++ redistributable 包即可正常导入 dolphindb 包。

如果使用的是 Windows 64-bit, 请从以下链接下载并安装 x86 和 x64 版本的 Visual C++ redistributable 包：

[vc\_redist.x64.exe](https://aka.ms/vs/16/release/vc_redist.x64.exe)（x64 安装程序）

[vc\_redist.x86.exe](https://aka.ms/vs/16/release/vc_redist.x86.exe)（x86 安装程序）

若执行完上述操作后，仍无法安装或导入，可在 [DolphinDB 社区](https://ask.dolphindb.net)中进行反馈。
