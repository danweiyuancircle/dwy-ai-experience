import type { HTMLAttributes } from 'vue'

export interface EImageProps {
  class?: HTMLAttributes['class']
  src?: string
  alt?: string
  fit?: 'contain' | 'cover' | 'fill' | 'none' | 'scale-down'
  lazy?: boolean
  fallback?: string
  preview?: boolean
}
