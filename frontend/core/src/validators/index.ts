/** Chinese mobile phone number */
export function isPhone(value: string): boolean {
  return /^1[3-9]\d{9}$/.test(value)
}

/** Email */
export function isEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
}

/** Chinese ID card (18 digits) */
export function isIdCard(value: string): boolean {
  return /^\d{17}[\dXx]$/.test(value)
}

/** URL */
export function isUrl(value: string): boolean {
  try { new URL(value); return true } catch { return false }
}

/** Non-empty string */
export function isRequired(value: any): boolean {
  if (value === null || value === undefined) return false
  if (typeof value === 'string') return value.trim().length > 0
  if (Array.isArray(value)) return value.length > 0
  return true
}

/** Min length */
export function minLength(value: string, min: number): boolean {
  return value.length >= min
}

/** Max length */
export function maxLength(value: string, max: number): boolean {
  return value.length <= max
}
