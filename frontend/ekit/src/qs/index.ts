import QS from 'qs'
import type { IStringifyOptions, IParseOptions } from 'qs'

export type { IStringifyOptions, IParseOptions }

const defaultStringifyOptions: IStringifyOptions = {
  arrayFormat: 'repeat',
  addQueryPrefix: false,
}

const defaultParseOptions: IParseOptions = {
  ignoreQueryPrefix: true,
}

export function stringify(obj: Record<string, any>, options?: IStringifyOptions): string {
  return QS.stringify(obj, { ...defaultStringifyOptions, ...options })
}

export function parse(str: string, options?: IParseOptions): Record<string, any> {
  return QS.parse(str, { ...defaultParseOptions, ...options }) as Record<string, any>
}
