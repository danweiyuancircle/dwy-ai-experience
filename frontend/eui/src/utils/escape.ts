const htmlEscapeMap: Record<string, string> = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  '\'': '&#039;',
}

export function escapeHtml(text: string): string {
  return text.replace(/[&<>"']/g, (ch) => htmlEscapeMap[ch])
}
