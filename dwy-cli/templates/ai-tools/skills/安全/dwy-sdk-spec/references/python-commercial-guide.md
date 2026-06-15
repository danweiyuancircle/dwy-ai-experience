# Python 商业版 SDK 完整打包指南

目标：发布到 PyPI 的 wheel 内**不含 `.py` 源文件**，只含编译后的 `.so` 与必要类型存根。

## 决策树

```
模块类型
├── 公开 API 入口（如 mypkg/__init__.py）→ 保留 .py（用户要 import）
├── 内部实现（_ 开头，如 mypkg/_engine.py）→ 编译为 .so
└── 类型存根（.pyi）→ 保留（用户 IDE 提示）
```

## 工具选择

| 工具 | 优势 | 推荐场景 |
|---|---|---|
| **Cython** | 成熟、setuptools 集成无缝、编译快 | **默认选择**，纯 Python → .so |
| Nuitka | 优化更激进、支持整包编译 | 大型业务逻辑、想编译整个包 |

下面以 Cython 为准。

## 项目结构示例

```
mypkg/                              # 包根目录
├── pyproject.toml
├── MANIFEST.in
├── .gitignore
├── src/
│   └── mypkg/
│       ├── __init__.py             # 公开入口（保留 .py，re-export）
│       ├── client.py               # 公开 API（保留 .py）
│       ├── _engine.py              # 内部核心（编译为 .so）
│       ├── _engine.pyi             # 类型存根（保留）
│       ├── _utils.py               # 内部工具（编译为 .so）
│       └── _utils.pyi              # 类型存根（保留）
```

## pyproject.toml 配置

```toml
[build-system]
requires = ["setuptools>=68.0", "Cython>=3.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mypkg"
version = "1.0.0"
requires-python = ">=3.11"

[tool.setuptools]
include-package-data = true
zip-safe = false

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
mypkg = ["*.pyi", "py.typed"]

[tool.setuptools.exclude-package-data]
mypkg = [
    "_*.py",        # 排除以 _ 开头的源文件（已编译为 .so）
    "*.c",          # Cython 中间产物
    "*.pyx",        # Cython 源
    "*.pyc",
    "__pycache__/*",
]
```

## setup.py（Cython 入口）

```python
from setuptools import setup
from Cython.Build import cythonize
from pathlib import Path

# 找所有 _ 开头的 .py 模块（命名约定：内部模块用 _ 前缀）
internal_modules = [
    str(p) for p in Path("src/mypkg").glob("_*.py")
    if p.name != "__init__.py"
]

setup(
    ext_modules=cythonize(
        internal_modules,
        compiler_directives={"language_level": "3"},
    ),
)
```

## MANIFEST.in

```
graft src
include README.md LICENSE py.typed
include src/mypkg/*.pyi

# 全局排除源码与中间产物
global-exclude _*.py
global-exclude *.pyx *.pxd *.c
global-exclude *.pyc *.pyo
global-exclude __pycache__ .DS_Store
```

`graft src` 含整个 src/，然后 `global-exclude _*.py` 排掉内部源；公开 `.py` 保留（如 `__init__.py` / `client.py` 不以 `_` 开头）。

## 构建命令

```bash
# 清理旧产物
rm -rf build/ dist/ src/*.egg-info/

# 编译 + 打包
python -m build

# 验证 wheel 内不含 _ 开头的 .py
unzip -l dist/*.whl | grep -E '_.*\.py$' && echo "FAIL: source leaked" || echo "OK"
```

## 验收清单（流程 B 用）

| 检查项 | 命令 |
|---|---|
| pyproject.toml 含 Cython | `grep -E 'cython\|Cython' pyproject.toml` |
| `_*.so` 存在 | `find src -name '_*.so' -type f` 应该有输出 |
| MANIFEST.in 排除源码 | `grep -E 'global-exclude.*_\*\.py' MANIFEST.in` |
| wheel 内无 `_*.py` | `unzip -l dist/*.whl \| grep -E '_.*\.py$'` 应该为空 |
| .gitignore 含编译产物 | `grep -E '^\*\.so\b\|^build/\b\|^dist/\b' .gitignore` |

## 常见踩坑

| 现象 | 原因 | 修复 |
|---|---|---|
| wheel 里有 `.py` 源 | `exclude-package-data` 没匹配到 / MANIFEST.in 缺 global-exclude | 同时配 setup 配置 + MANIFEST.in |
| 装完后 `ImportError: cannot import name '_engine'` | `__init__.py` 用了 `from . import _engine` 但 .so 命名空间不对 | 确保 `.so` 文件在包内，名字与 import 路径一致 |
| `pip install -e .` 后 import 慢 | 开发模式没编译 .so，跑了 .py | 开发用 `python setup.py build_ext --inplace` 触发编译 |
| 跨平台 wheel（manylinux / macOS） | 单平台编译产物只能装到对应平台 | 用 `cibuildwheel`（项目已有 dwy-github-action-publish skill） |

## 参考 dwy-shared 内已有 SDK

`backend/`（`dwyeapi`）当前是**开源版**（pyproject.toml 无 Cython 配置）。若要转商业版：
1. 把 `src/dwyeapi/security.py` / `database.py` 重命名为 `_security.py` / `_database.py`
2. `__init__.py` 加 re-export 维持公开 API
3. 加 Cython 配置、MANIFEST.in、setup.py
4. 重新发布 → 装完后用户 import 路径不变，但拿不到 .py 源
