/** 验证 iOS App Store 发布 Skill 的私有配置与模板约束。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'

/** 将回调式进程执行接口转换为 Promise，供测试等待脚本完成。 */
const execFileAsync = promisify(execFile)

/** Skill 模板目录；测试在发布模板存在时验证其可同步约束。 */
const skillDir = path.resolve('templates/ai-tools/skills/发布发版/dwy-ios-app-store-release')

/** 使用隔离临时目录运行配置脚本，避免接触真实用户凭据。 */
async function runConfig(args, root) {
  const script = path.join(skillDir, 'scripts/appstore_config.sh')
  return execFileAsync('bash', [script, ...args, '--root', root], { cwd: process.cwd() })
}

test('appstore_config 保存非秘密标识且可重置', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-appstore-config-'))
  t.after(() => fs.remove(root))

  await runConfig(['init'], root)
  await runConfig(['set', '--issuer-id', 'issuer-1', '--key-id', 'key-1', '--team-id', 'team-1'], root)

  const configPath = path.join(root, 'config.json')
  assert.deepEqual(await fs.readJson(configPath), {
    version: 1,
    issuer_id: 'issuer-1',
    key_id: 'key-1',
    team_id: 'team-1',
  })

  await runConfig(['reset'], root)
  assert.equal(await fs.pathExists(configPath), false)
})

test('发布模板声明双语、全地区与 ICP 非阻塞策略', async () => {
  const skill = await fs.readFile(path.join(skillDir, 'SKILL.md'), 'utf8')
  const submission = await fs.readFile(path.join(skillDir, 'assets/appstore-submission.yaml'), 'utf8')
  const reviewScreenshot = await fs.readFile(path.join(skillDir, 'references/in-app-purchase-review.md'), 'utf8')

  assert.match(skill, /zh-Hans/)
  assert.match(skill, /en-US/)
  assert.match(skill, /二次确认/)
  assert.match(skill, /ICP/)
  assert.match(submission, /all_territories/)
  assert.match(submission, /not_started/)
  assert.match(reviewScreenshot, /1280 × 800/)
})
