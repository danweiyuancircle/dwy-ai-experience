# PyPI / npm 发布黑名单

`check_python_publish.sh` / `check_js_publish.sh` 的规则源。

## Python（PyPI）

### 商业版：白名单（其他一律违规）

| 允许的文件 / 模式 | 说明 |
|---|---|
| `*.so` | 编译产物 |
| `*.pyi` | 类型存根（无源） |
| `py.typed` | 标记包支持类型检查 |
| `*.dist-info/**` | wheel 元数据（METADATA / RECORD / WHEEL / entry_points.txt 等） |
| `LICENSE` `LICENSE.*` `LICENCE` | 许可证（可在包外） |
| `README` `README.*` | 仅 dist-info 内 |
| `<pkg>/__init__.py` | 公开入口（如果用了 re-export 模式） |
| `<pkg>/<public_module>.py` | 不以 `_` 开头的公开 API 模块 |
| 业务必要资源（图片、json、模板） | 列入 `package-data` |

### 开源版：黑名单（任意命中视为违规）

| 禁止的文件 / 模式 | 原因 |
|---|---|
| `__pycache__/**` | 字节码缓存，可反编译 |
| `*.pyc` `*.pyo` | 同上 |
| `*.egg-info/**` | 旧式构建元数据，含本地路径 |
| `.mypy_cache/**` `.pytest_cache/**` `.ruff_cache/**` | 开发工具缓存 |
| `.pdb` `.idb` | 调试符号 |
| `.env` `.env.*` `.env.local` | 环境变量（凭证） |
| `.pypirc` | PyPI 凭证（致命） |
| `.git/**` `.gitignore` | 版本控制（含历史） |
| `.DS_Store` `Thumbs.db` | 系统文件 |
| `.vscode/**` `.idea/**` | IDE 配置（可能含路径） |
| `*.bak` `*.swp` `*.swo` `*~` | 编辑器临时文件 |

## npm

### 商业版：白名单（其他一律违规）

| 允许的文件 / 模式 | 说明 |
|---|---|
| `dist/**` | 构建产物（minified） |
| `package.json` | 必有 |
| `README` `README.*` | 用户必读 |
| `LICENSE` `LICENSE.*` `LICENCE` | 许可证 |
| `CHANGELOG` `CHANGELOG.*` | 可选 |
| `bin/**` | 仅 CLI 包 |
| `*.d.ts` 在 dist/ 内 | 类型定义 |

### 开源版：黑名单（任意命中视为违规）

| 禁止的文件 / 模式 | 原因 |
|---|---|
| `src/**` `tests/**` `__tests__/**` | 源码 / 测试（占体积） |
| `*.test.ts` `*.spec.ts` `*.test.js` `*.spec.js` | 测试文件 |
| `*.map` `*.js.map` `*.d.ts.map` | sourcemap（源码可还原） |
| `*.tsbuildinfo` | TS 增量编译信息（含路径） |
| `tsconfig*.json` | 编译配置 |
| `vite.config.*` `vitest.config.*` `tsup.config.*` `rollup.config.*` `webpack.config.*` | 打包配置 |
| `.eslintrc*` `.prettierrc*` `eslint.config.*` `prettier.config.*` | Lint 配置 |
| `.env` `.env.*` | 环境变量（凭证） |
| `.npmrc` `.yarnrc` `.pnpmrc` | 包管理器配置（含 token） |
| `.git/**` `.gitignore` `.gitattributes` | 版本控制 |
| `.github/**` `.gitlab-ci.yml` `.travis.yml` `.circleci/**` | CI 配置（含 secret 引用） |
| `.vscode/**` `.idea/**` `*.swp` | IDE / 编辑器 |
| `.DS_Store` `Thumbs.db` | 系统文件 |
| `node_modules/**` | 依赖（npm 自动忽略，但 .npmignore 错误时可能漏出） |
| `pnpm-lock.yaml` `package-lock.json` `yarn.lock` | 锁文件（npm 默认忽略） |
| `.husky/**` `commitlint.config.*` | Git hook 配置 |

## 致命级（任何版本都禁）

无论商业 / 开源，下列文件一旦发到 PyPI / npm 都视为**严重事故**，必须立即 `npm unpublish` / 联系 PyPI 删除：

| 文件 | 风险 |
|---|---|
| `.env*` | 含 API key / DB 密码 / 第三方凭证 |
| `.npmrc` `.pypirc` `.git-credentials` | 仓库 / 包管理器登录凭证 |
| `id_rsa` `id_ed25519` `*.pem` `*.key` `*.p12` | SSH / TLS 私钥 |
| `secrets.json` `credentials.json` `.aws/credentials` | 云服务凭证 |
| `*.pdb` 含调试源 / `.dSYM` | 调试符号文件 |

`check_*_publish.sh` 命中致命级 → 输出 `[CRITICAL]` 并提示用户立即从 registry 下架。

## 校验自动化

每次 `pre-publish` 钩子建议接 skill：

**Python**（`pyproject.toml`）：

```toml
# 暂无标准 prepublish hook，推荐 Makefile / justfile
```

**npm**（`package.json`）：

```json
{
  "scripts": {
    "prepublishOnly": "pnpm build && npm pack --dry-run && dwy-sdk-spec check"
  }
}
```

（注：`dwy-sdk-spec check` 是未来 CLI 子命令计划，当前在 Claude Code 中触发 skill）
