#!/bin/bash
# 单独保留宿主输入，Python 脚本从 here-document 读取。
exec python3 - 3<&0 <<'PY'
import json
import os
import re
import shlex
import subprocess
import sys

event = json.load(os.fdopen(3))
tool = event.get("tool_input", {})
command = tool.get("command", tool.get("cmd", ""))
if not re.search(r"\bgit\s+(?:(?:-C|-c)\s+(?:\"[^\"]*\"|'[^']*'|\S+)\s+)*commit\b", command):
    sys.exit(0)

def block(message):
    print(message, file=sys.stderr)
    sys.exit(2)

lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()<>")
lexer.whitespace_split = True
lexer.commenters = ""
tokens = list(lexer)
if "commit" not in tokens:
    sys.exit(0)
if any(re.fullmatch(r"[;&|()<>]+", token) for token in tokens):
    block("请分开执行暂存与提交，在目标仓库单独运行 git commit，以便检查实际暂存内容。")

args = tokens[tokens.index("git") + 1:] if "git" in tokens else []
if "commit" not in args:
    sys.exit(0)
before, after = args[:args.index("commit")], args[args.index("commit") + 1:]
approval = None
directory = tool.get("workdir") or event.get("cwd") or os.getcwd()
while before:
    option = before.pop(0)
    if option == "-C" and before:
        directory = os.path.join(directory, before.pop(0))
    elif option == "-c" and before:
        setting = before.pop(0)
        if setting.startswith("dwy.testcodeConfirmed="):
            approval = setting.split("=", 1)[1]
    else:
        block("请在目标仓库单独执行 git commit，以便检查暂存区。")

# 路径提交、-a 和交互式提交可在 hook 运行后改变提交内容。
i = 0
while i < len(after):
    arg = after[i]
    if arg in ("-m", "-F", "-C", "-c", "--message", "--file", "--reuse-message",
               "--reedit-message", "--author", "--date", "--trailer", "--fixup", "--squash"):
        i += 2
        continue
    if (arg == "--" or not arg.startswith("-") or arg in ("--all", "--include", "--only",
            "--interactive", "--patch") or arg.startswith("--pathspec-from-file")
            or re.match(r"^-[^-]*[aipo]", arg) and not arg.startswith(("-m", "-F", "-C", "-c", "-S"))):
        block("请先单独 git add，再从暂存区提交，以便检查临时测试代码。")
    i += 1

def git(*args, **kwargs):
    return subprocess.run(["git", "--literal-pathspecs", *args], cwd=directory,
                          stdout=subprocess.PIPE, **kwargs)

paths = git("diff", "--cached", "--name-only", "--diff-filter=ACMRT", "-z", check=True).stdout.split(b"\0")[:-1]
marker = (r"^[[:space:]]*(//+|/\*+|\*|#+|--|<!--)[[:space:]]*"
          r"(TESTCODE([[:space:]:：]|$)|MOCK[[:space:]]*([:：]|(\*/|-->)?[[:space:]]*$))")
hits = []
for start in range(0, len(paths), 64):
    result = git("grep", "--cached", "-n", "-I", "-i", "-E", "-e", marker, "--", *paths[start:start + 64])
    if result.returncode == 0:
        hits.append(os.fsdecode(result.stdout).rstrip())
    elif result.returncode != 1:
        block("暂存区读取失败，无法检查 TESTCODE 或 MOCK 标记。")
if hits:
    tree = git("write-tree", check=True).stdout.decode().strip()
    if approval != tree:
        block("暂存文件含临时测试代码：\n" + "\n".join(hits)
              + "\n请移除整个测试片段并重新暂存，或向用户确认是否保留这些具体改动。"
              + "\n仅在明确同意后，用 git -c dwy.testcodeConfirmed=" + tree + " commit 提交。")
PY
