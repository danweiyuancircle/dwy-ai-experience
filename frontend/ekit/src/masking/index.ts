/**
 * PII 数据脱敏工具
 * 用于前端展示敏感字段时打码（手机/邮箱/身份证/银行卡/姓名/地址/IP/车牌）
 * 输入不符合格式时原样返回，不抛错，方便直接用在模板里
 */

/**
 * 手机号脱敏：前3后4，中间 ****
 * @example maskPhone('13812345678') → '138****5678'
 */
export function maskPhone(phone: string): string {
  // 非 11 位数字视为无效手机号，直接原样返回
  if (!phone || !/^\d{11}$/.test(phone)) return phone
  return `${phone.slice(0, 3)}****${phone.slice(-4)}`
}

/**
 * 邮箱脱敏：首字符 + *** + @域名
 * @example maskEmail('zhangsan@gmail.com') → 'z***@gmail.com'
 */
export function maskEmail(email: string): string {
  if (!email) return email
  const match = email.match(/^([^@]+)@([^@]+)$/)
  if (!match) return email
  return `${match[1][0]}***@${match[2]}`
}

/**
 * 身份证脱敏：前3后4，中间用 * 补齐
 * @example maskIdCard('420106199901011234') → '420***********1234'
 */
export function maskIdCard(idCard: string): string {
  if (!idCard || !/^\d{17}[\dXx]$/.test(idCard)) return idCard
  return `${idCard.slice(0, 3)}***********${idCard.slice(-4)}`
}

/**
 * 银行卡脱敏：前4后4，中间用 * 补齐
 * @example maskBankCard('6222021234561234') → '6222********1234'
 */
export function maskBankCard(card: string): string {
  // 银行卡长度 13~19 位，超出范围按无效处理
  if (!card || !/^\d{13,19}$/.test(card)) return card
  const maskLen = card.length - 4 - 4
  return `${card.slice(0, 4)}${'*'.repeat(maskLen)}${card.slice(-4)}`
}

/**
 * 姓名脱敏：2字 → 姓+*；3+字 → 姓+*×(n-2)+末字
 * @example maskName('张三') → '张*'
 * @example maskName('张三明') → '张*明'
 */
export function maskName(name: string): string {
  if (!name || name.length <= 1) return name
  if (name.length === 2) return `${name[0]}*`
  return `${name[0]}${'*'.repeat(name.length - 2)}${name[name.length - 1]}`
}

/**
 * 地址脱敏：匹配行政区划后 + ****，不匹配时保留前6字符 + ****
 * @example maskAddress('浙江省杭州市西湖区文三路100号') → '浙江省杭州市西湖区****'
 */
export function maskAddress(address: string): string {
  if (!address) return address
  // 贪婪匹配连续的省/市/区/县/镇/旗/自治区前缀，保留完整行政区划
  const regionRe = /^((?:.*(?:省|自治区|市|区|县|镇|旗))+)/
  const match = address.match(regionRe)
  if (match) {
    return `${match[1]}****`
  }
  // 识别不出行政区划时，按长度保留前 6 个字符
  if (address.length < 6) return address
  return `${address.slice(0, 6)}****`
}

/**
 * IP 脱敏：末段替换 *
 * @example maskIp('192.168.1.100') → '192.168.1.*'
 */
export function maskIp(ip: string): string {
  if (!ip) return ip
  const parts = ip.split('.')
  // 仅处理 IPv4（四段）；IPv6 或异常格式原样返回
  if (parts.length !== 4) return ip
  return `${parts[0]}.${parts[1]}.${parts[2]}.*`
}

/**
 * 车牌号脱敏：前2后1，中间 ***
 * @example maskLicensePlate('浙A12348') → '浙A***8'
 */
export function maskLicensePlate(plate: string): string {
  // 车牌至少 7 位（普通车牌 7 位，新能源 8 位）
  if (!plate || plate.length < 7) return plate
  return `${plate.slice(0, 2)}***${plate[plate.length - 1]}`
}

/**
 * 通用文本脱敏：保留首尾 N 位，中间用 maskChar 替换
 * @param text 原始文本
 * @param start 保留头部字符数，默认 1
 * @param end 保留尾部字符数，默认 1
 * @param maskChar 脱敏字符，默认 '*'
 * @example maskText('hello') → 'h***o'
 */
export function maskText(
  text: string,
  start = 1,
  end = 1,
  maskChar = '*',
): string {
  if (!text) return text
  // 文本长度不够保留首尾时，原样返回避免脱敏成空串
  if (text.length <= start + end) return text
  const maskLen = text.length - start - end
  return `${text.slice(0, start)}${maskChar.repeat(maskLen)}${text.slice(text.length - end || undefined)}`
}
