/**
 * HTML 文本转义工具
 * 命令式 UI（useMessage / useMessageBox / useNotification）通过 innerHTML 拼接，
 * 必须对用户输入做转义以防 XSS
 */

/** HTML 特殊字符到实体的映射 */
const htmlEscapeMap: Record<string, string> = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  '\'': '&#039;',
}

/**
 * 转义 HTML 文本中的特殊字符，防止注入
 * @param text 原始文本
 * @returns 转义后的安全字符串
 */
export function escapeHtml(text: string): string {
  return text.replace(/[&<>"']/g, (ch) => htmlEscapeMap[ch])
}
