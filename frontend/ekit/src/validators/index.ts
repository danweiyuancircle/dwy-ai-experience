import { phoneSchema, emailSchema, idCardSchema, urlSchema, requiredSchema, minLengthSchema, maxLengthSchema } from './schemas'

/** Chinese mobile phone number */
export function isPhone(value: string): boolean {
  return phoneSchema.safeParse(value).success
}

/** Email */
export function isEmail(value: string): boolean {
  return emailSchema.safeParse(value).success
}

/** Chinese ID card (18 digits) */
export function isIdCard(value: string): boolean {
  return idCardSchema.safeParse(value).success
}

/** URL */
export function isUrl(value: string): boolean {
  return urlSchema.safeParse(value).success
}

/** Non-empty string */
export function isRequired(value: any): boolean {
  return requiredSchema.safeParse(value).success
}

/** Min length */
export function minLength(value: string, min: number): boolean {
  return minLengthSchema(min).safeParse(value).success
}

/** Max length */
export function maxLength(value: string, max: number): boolean {
  return maxLengthSchema(max).safeParse(value).success
}

// Re-export schemas
export { phoneSchema, emailSchema, idCardSchema, urlSchema, requiredSchema, minLengthSchema, maxLengthSchema } from './schemas'
