# create-dwy

## 0.13.4

### Patch Changes

- 默认模板仓库源改为 GitHub：`DWY_REPO_URL` 从 `https://gitee.com/snailyuanyuan/dwy-shared.git` 切换为 `https://github.com/danweiyuancircle/dwy-shared.git`，确保 `dwy` CLI 同步链路只跟踪 GitHub。

## 0.13.2

### Patch Changes

- 新增顶层命令 `dwy sync`，一次选择后同时同步 Claude Code 与 Codex 配置。
- `dwy sync -i` 支持重新交互式选择；`dwy sync --dry-run` 支持预演；`dwy sync md` 同步 `CLAUDE.md` 到 `~/.claude/CLAUDE.md` 和 `~/.codex/AGENTS.md`。
- 复用现有 `dwy claude sync` / `dwy codex sync` 的扫描、缓存选择、删除未选模板项和写入逻辑；`commands` 仅同步到 `.claude/commands`，`skills` / `rules` / `hooks` 同步到两端。
- 新增 CLI 聚合同步回归测试，覆盖一次缓存选择同时写入 `.claude`、`.agents`、`.codex` 和 `AGENTS.md`。
